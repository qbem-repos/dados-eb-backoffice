# Deploy Docker — qbem-backoffice-eb

> Guia de referência para build da imagem Docker e atualização do pacote privado `shareds`.

---

## Sumário

1. [Pré-requisitos](#1-pré-requisitos)
2. [Estrutura de arquivos de deploy](#2-estrutura-de-arquivos-de-deploy)
3. [Variáveis de Ambiente](#3-variáveis-de-ambiente)
4. [Por que o `shareds` usa wheel local?](#4-por-que-o-shareds-usa-wheel-local)
5. [Build manual da imagem](#5-build-manual-da-imagem)
6. [Subir o container manualmente](#6-subir-o-container-manualmente)
7. [Fluxo automatizado com `update_shareds.ps1`](#7-fluxo-automatizado-com-update_sharedsps1)
8. [Atualizar o `shareds` e fazer novo deploy](#8-atualizar-o-shareds-e-fazer-novo-deploy)
9. [Modos de execução (`APP_ENV`)](#9-modos-de-execução-app_env)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Pré-requisitos

| Ferramenta | Versão mínima | Observação |
|---|---|---|
| Docker Desktop | 4.x | Deve estar em execução |
| Python | 3.13 | Usado pelo venv local para gerar o wheel |
| Git | qualquer | Necessário para clonar o `shareds` localmente |
| Acesso ao GitHub | — | Repositório `qbem-repos/dados-py-shareds` |

---

## 2. Estrutura de arquivos de deploy

```
qbem_backoffice_eb/
├── Dockerfile              # Definição da imagem
├── .dockerignore           # Arquivos ignorados no build
├── .env                    # Variáveis de ambiente (nunca commitar)
├── requirements.txt        # Dependências Python fixadas
├── wheels/
│   └── shareds-*.whl       # Wheel do pacote privado (gerado localmente)
├── scripts/
│   └── update_shareds.ps1  # Script de atualização e deploy
└── main.py                 # Entrypoint da API
```

---

## 3. Variáveis de Ambiente

O arquivo `.env` na raiz do projeto deve conter as seguintes variáveis:

```dotenv
# Ambiente de execução (production | development)
ENVIRONMENT=HOMOLOG

# PostgreSQL
POSTGRES_HOST=<host>
POSTGRES_PORT=5432
POSTGRES_USER=<user>
POSTGRES_PASSWORD=<password>

# Segurança da API
JWT_SECRET=<secret>
JWT_ALGORITHM=HS256

# ClickHouse (se utilizado)
CLICKHOUSE_HOST=<host>
CLICKHOUSE_PORT=9000
CLICKHOUSE_USERNAME=<user>
CLICKHOUSE_PASSWORD=<password>
```

> ⚠️ O arquivo `.env` está no `.gitignore` e **não deve ser versionado**.

Para passar as variáveis ao container, use o flag `--env-file`:

```powershell
docker run --env-file .env ...
```

---

## 4. Por que o `shareds` usa wheel local?

O pacote `shareds` é hospedado em um repositório **GitHub privado** (`qbem-repos/dados-py-shareds`). O Docker, durante o build, não tem acesso às credenciais do usuário, portanto o `pip install git+https://...` falha dentro do container.

A solução adotada é:

1. Gerar o `.whl` **localmente** (onde há acesso autenticado ao Git).
2. Copiar o arquivo `.whl` para a pasta `wheels/`.
3. Instalar a partir do arquivo local dentro do container.

```
[Dev local] git clone shareds → gera .whl → wheels/shareds-X.Y.Z.whl
                                                         ↓
[Docker build]  COPY wheels/ → pip install wheels/shareds-*.whl
```

---

## 5. Build manual da imagem

> Use este fluxo apenas quando **não** quiser usar o script automatizado.

### 5.1 Garantir que o wheel do `shareds` está atualizado

```powershell
# Na raiz do projeto, com o venv ativado
.venv\Scripts\python.exe -m pip wheel --no-deps --wheel-dir wheels `
  git+https://github.com/qbem-repos/dados-py-shareds.git@master
```

### 5.2 Construir a imagem

```powershell
docker build -t qbem-backoffice-eb .
```

O Dockerfile executa as seguintes etapas:

| Etapa | Descrição |
|---|---|
| `FROM python:3.13-slim` | Imagem base leve com Python 3.13 |
| `apt-get install build-essential libpq-dev git` | Dependências de sistema para compilar `psycopg2` |
| `COPY wheels/` | Copia o wheel do `shareds` |
| `pip install -r requirements_filtered.txt` | Instala dependências públicas (sem a linha `-e` e sem `shareds`) |
| `pip install wheels/shareds-*.whl` | Instala o `shareds` via wheel local |
| `COPY . .` | Copia o código-fonte |
| `pip install .` | Instala o próprio pacote `qbem-backoffice-eb` |

---

## 6. Subir o container manualmente

```powershell
docker run -d `
  --name qbem-backoffice-eb `
  -p 8001:8000 `
  --env-file .env `
  qbem-backoffice-eb
```

Verificar logs:

```powershell
docker logs qbem-backoffice-eb
```

Saída esperada:

```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

A API ficará disponível em:

- **Swagger UI:** `http://localhost:8001/backoffice/v1/docs`
- **ReDoc:** `http://localhost:8001/backoffice/v1/redoc`

---

## 7. Fluxo automatizado com `update_shareds.ps1`

O script `scripts/update_shareds.ps1` automatiza todo o processo em um único comando.

### Parâmetros

| Parâmetro | Tipo | Descrição |
|---|---|---|
| *(nenhum)* | — | Apenas atualiza o wheel local |
| `-Rebuild` | switch | Atualiza o wheel + rebuild da imagem Docker |
| `-Up` | switch | (requer `-Rebuild`) Para e sobe o container após o build |
| `-Port` | string | Porta do host a mapear (padrão: `8001`) |

### O que o script faz (passo a passo)

```
[1/5] Remove wheels antigos do shareds em wheels/
[2/5] Clona e gera novo wheel via pip wheel
[3/5] Identifica o .whl gerado e atualiza a referência no Dockerfile
[4/5] Executa docker build (se -Rebuild)
[5/5] Para o container anterior e sobe o novo (se -Up)
```

---

## 8. Atualizar o `shareds` e fazer novo deploy

### Cenário 1 — Apenas atualizar o wheel (sem rebuild)

Útil para preparar o artefato antes de um deploy planejado:

```powershell
.\scripts\update_shareds.ps1
```

### Cenário 2 — Atualizar wheel + rebuild da imagem

```powershell
.\scripts\update_shareds.ps1 -Rebuild
```

### Cenário 3 — Atualizar + rebuild + subir o container (deploy completo)

```powershell
.\scripts\update_shareds.ps1 -Rebuild -Up
```

### Cenário 4 — Deploy completo em porta customizada

```powershell
.\scripts\update_shareds.ps1 -Rebuild -Up -Port 8080
```

---

## 9. Modos de execução (`APP_ENV`)

A variável `APP_ENV` controla o comportamento do `uvicorn`:

| Valor | Reload automático | Uso |
|---|---|---|
| `production` *(padrão)* | ❌ | Containers / servidores |
| `development` | ✅ | Desenvolvimento local |

Para rodar localmente com reload:

```powershell
$env:APP_ENV = "development"
python main.py
```

---

## 10. Troubleshooting

### `docker daemon is not running`

O Docker Desktop não está iniciado.

```powershell
Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
# Aguarde ~30s e tente novamente
```

---

### `port is already allocated`

A porta escolhida já está em uso. Pare o container anterior ou use outra porta:

```powershell
docker rm -f qbem-backoffice-eb
# ou use outra porta:
.\scripts\update_shareds.ps1 -Rebuild -Up -Port 8002
```

---

### `ModuleNotFoundError: No module named 'asyncpg'`

O `asyncpg` não está no `requirements.txt`. Adicione e faça rebuild:

```powershell
# Verificar versão instalada no venv
.venv\Scripts\python.exe -m pip show asyncpg

# Adicionar ao requirements.txt e rebuildar
.\scripts\update_shareds.ps1 -Rebuild -Up
```

---

### `TypeError: can only concatenate str (not "NoneType") to str`

A variável `ENVIRONMENT` não está definida. Verifique se o `--env-file .env` foi passado corretamente e se o `.env` contém `ENVIRONMENT=<valor>`.

---

### `fatal: could not read Username for 'https://github.com'`

O Git não tem acesso ao repositório privado `shareds` dentro do container. Certifique-se de **sempre usar o script** ou gerar o wheel manualmente antes do build. O wheel deve existir em `wheels/shareds-*.whl` antes de executar `docker build`.
