# Arquitetura Base — Serviços Qbem (Dados)

> Documento de referência para reprodução da arquitetura em novos serviços que seguem o mesmo padrão.  
> Projeto de origem: `qbem-backoffice-eb`

---

## Sumário

1. [Visão Geral](#1-visão-geral)
2. [Estrutura de Pastas](#2-estrutura-de-pastas)
3. [Camadas da Arquitetura](#3-camadas-da-arquitetura)
   - 3.1 [Config — Variáveis de Ambiente](#31-config--variáveis-de-ambiente)
   - 3.2 [Data — Modelos e Banco de Dados](#32-data--modelos-e-banco-de-dados)
   - 3.3 [Application — Lógica de Negócio (Services)](#33-application--lógica-de-negócio-services)
   - 3.4 [API REST — Endpoints FastAPI](#34-api-rest--endpoints-fastapi)
4. [Biblioteca Compartilhada: `shareds`](#4-biblioteca-compartilhada-shareds)
5. [Segurança e Autenticação](#5-segurança-e-autenticação)
6. [Padrão de Service com Inner Classes](#6-padrão-de-service-com-inner-classes)
7. [Padrão de Tratamento de Erros](#7-padrão-de-tratamento-de-erros)
8. [Banco de Dados e Migrations (Alembic)](#8-banco-de-dados-e-migrations-alembic)
9. [Testes](#9-testes)
10. [Variáveis de Ambiente](#10-variáveis-de-ambiente)
11. [Dependências](#11-dependências)
12. [Guia de Reprodução em Novo Serviço](#12-guia-de-reprodução-em-novo-serviço)

---

## 1. Visão Geral

Os serviços da plataforma Qbem (módulo Dados) seguem uma **arquitetura em camadas** com separação clara de responsabilidades:

```
API REST  →  Application (Service)  →  Data (Model / DB Session)
```

- **FastAPI** como framework HTTP assíncrono.
- **SQLAlchemy 2.x (async)** para acesso ao banco de dados.
- **PostgreSQL** como banco relacional, organizado em **schemas**.
- **Alembic** para versionamento e migração de schema.
- **Pydantic v2** para validação de entrada/saída em todas as camadas.
- **`shareds`** (biblioteca interna privada) fornece segurança, autenticação JWT, exceções padronizadas e mixins para modelos.

---

## 2. Estrutura de Pastas

```
<nome-do-servico>/
├── main.py                          # Entrypoint (placeholder)
├── pyproject.toml                   # Metadados do projeto (uv/pip)
├── requirements.txt                 # Dependências fixadas
│
├── config/                          # Configuração e variáveis de ambiente
│   ├── getenv.py                    # Classe principal GetEnv
│   └── getenv_mixins/
│       ├── db_postgres_connection.py  # Mixin com URLs de conexão PostgreSQL
│       └── validate_env.py            # Mixin de validação de variáveis
│
├── src/
│   ├── api_rest/                    # Camada HTTP (FastAPI)
│   │   ├── main.py                  # App raiz — monta sub-aplicações com prefixos
│   │   └── v1/
│   │       ├── main.py              # App da versão v1 — inclui todos os routers
│   │       └── endpoints/           # Um arquivo por recurso de domínio
│   │           ├── <recurso>.py
│   │           └── ...
│   │
│   ├── application/                 # Camada de lógica de negócio
│   │   └── <dominio>/               # Ex: rpas/
│   │       ├── <entidade>.py        # Uma classe Service por entidade
│   │       └── ...
│   │
│   └── data/
│       └── db_<nome_db>/            # Um diretório por banco de dados
│           ├── db_session.py        # Engines e fábrica de sessões
│           ├── create_db_and_schemas.py  # Script de provisionamento inicial
│           ├── alembic.ini          # Config do Alembic (localizado junto ao banco)
│           ├── env.py               # Env do Alembic
│           ├── script.py.mako       # Template de revisão Alembic
│           ├── models/
│           │   ├── _base_model.py   # BaseModel com campos de auditoria
│           │   ├── _all_models.py   # Re-exporta todos os modelos (usado pelo Alembic)
│           │   └── <dominio>.py     # Modelos SQLAlchemy por domínio
│           └── versions/            # Arquivos de migração Alembic
│
└── tests/
    ├── __init__.py
    ├── conftest.py                  # Fixtures: db_session, user_scope
    ├── _tests_config.py             # Helpers: build_superadmin_scope, factories
    └── application/
        └── <dominio>/
            └── test_<entidade>.py
```

---

## 3. Camadas da Arquitetura

### 3.1 Config — Variáveis de Ambiente

**Arquivo principal:** `config/getenv.py`

```python
from config.getenv_mixins.db_postgres_connection import _PostgresConnection
from config.getenv_mixins.validate_env import ValidateEnvMixin
from shareds.config.getenv import SharedsGetEnv

class GetEnv(ValidateEnvMixin, SharedsGetEnv):
    class DB_NomeDoServico(_PostgresConnection):
        DB: str = "nome_db_" + os.getenv("ENVIRONMENT")
```

**Regras:**
- Cada banco de dados é representado como uma **inner class** dentro de `GetEnv`, herdando `_PostgresConnection`.
- O nome do banco inclui o sufixo do ambiente (`ENVIRONMENT`), ex: `backoffice_eb_dev`.
- `_PostgresConnection` lê `POSTGRES_HOST`, `POSTGRES_PORT`, `POSTGRES_USER` e `POSTGRES_PASSWORD` do ambiente e gera as URLs de conexão síncrona (`psycopg2`) e assíncrona (`asyncpg`).
- `ValidateEnvMixin.validate_all_env_vars()` pode ser chamado na inicialização para garantir que nenhuma variável está `None`.
- `SharedsGetEnv` (da lib `shareds`) centraliza configurações adicionais compartilhadas entre serviços.

---

### 3.2 Data — Modelos e Banco de Dados

#### BaseModel (`models/_base_model.py`)

Todo modelo SQLAlchemy herda de `BaseModel`, que adiciona **campos de auditoria** automáticos:

| Campo                 | Tipo       | Descrição                        |
|-----------------------|------------|----------------------------------|
| `created_at`          | `DateTime` | Data/hora de criação             |
| `created_by_user_id`  | `Integer`  | ID do usuário que criou          |
| `updated_at`          | `DateTime` | Data/hora da última atualização  |
| `updated_by_user_id`  | `Integer`  | ID do usuário que atualizou      |

`BaseModel` também herda `PydanticSchemaGeneratorMixin` (de `shareds`), que fornece o método de classe `.to_pydantic_schema()` para gerar automaticamente um schema Pydantic a partir das colunas do modelo SQLAlchemy — usado como `Output` em operações de leitura.

```python
from shareds.services.db_models_mixins.schema_generator import PydanticSchemaGeneratorMixin

class BaseModel(_Base, PydanticSchemaGeneratorMixin):
    __abstract__ = True
    created_at: Mapped[datetime] = mapped_column(DateTime, ...)
    created_by_user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    updated_by_user_id: Mapped[int] = mapped_column(Integer, nullable=True)
```

#### Modelos de Domínio (`models/<dominio>.py`)

- Cada arquivo de domínio define todos os modelos SQLAlchemy relacionados.
- Tabelas de **dimensão** (lookup) usam `nome: str` como **chave primária** (sem ID numérico).
- Tabelas de **entidade principal** usam `id: int` auto-incrementado.
- Todas as tabelas pertencem a um **schema PostgreSQL** declarado em `__table_args__`.
- Relacionamentos entre tabelas usam `ForeignKey` referenciando `schema.tabela.coluna`.

```python
class OperadoraModel(BaseModel):
    __tablename__ = "operadoras"
    __table_args__ = {"schema": "rpas"}
    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)

class RPAModel(BaseModel):
    __tablename__ = "rpas"
    __table_args__ = {"schema": "rpas"}
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    operadora_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.operadoras.nome"))
    # ...
```

#### DB Session (`db_session.py`)

Fornece duas engines (síncrona e assíncrona) e três formas de obter sessão:

| Função/Objeto                          | Uso                                                      |
|----------------------------------------|----------------------------------------------------------|
| `get_session(is_async=True)`           | Retorna uma sessão crua (sem gerenciamento de ciclo)     |
| `get_managed_session()`                | Context manager assíncrono com commit/rollback/close     |
| `get_async_db_session_dependency()`    | **Dependency Injection** para endpoints FastAPI          |

```python
# Nos endpoints, use sempre via Depends:
db_session: AsyncSession = Depends(get_async_db_session_dependency)
```

---

### 3.3 Application — Lógica de Negócio (Services)

Cada entidade de domínio possui **uma classe Service** em `src/application/<dominio>/<entidade>.py`. Ver detalhamento completo na [Seção 6](#6-padrão-de-service-com-inner-classes).

---

### 3.4 API REST — Endpoints FastAPI

#### Montagem da aplicação (`src/api_rest/`)

A app é composta em dois níveis:

1. **`src/api_rest/main.py`** — App raiz que monta versões como sub-aplicações com prefixo:
   ```python
   app.mount("/backoffice/v1", backoffice_app)
   ```

2. **`src/api_rest/v1/main.py`** — App da versão que inclui todos os routers:
   ```python
   app.include_router(operadoras.router)
   app.include_router(rpas.router)
   # ...
   ```

#### Endpoints (`src/api_rest/v1/endpoints/<recurso>.py`)

Cada arquivo de endpoint segue o padrão:

```python
router = APIRouter(tags=["NomeRecurso"], prefix="/nome-recurso")

def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})

@router.post("", response_model=RecursoService.Create.Output)
async def create_recurso(
    data: RecursoService.Create.Input,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await RecursoService.Create.create_recurso(data, user_scope, db_session, user_id=user_scope.user_id)
    return _to_output(model, RecursoService.Create.Output)
```

**Convenções dos endpoints:**

| Método | Path             | Operação             |
|--------|------------------|----------------------|
| POST   | `/recurso`       | Criar                |
| GET    | `/recurso`       | Listar todos         |
| GET    | `/recurso/{id}`  | Buscar por ID        |
| PUT    | `/recurso/{id}`  | Atualizar            |
| DELETE | `/recurso/{id}`  | Deletar              |
| GET    | `/recurso/bi`    | Dados para BI/dashboard |

---

## 4. Biblioteca Compartilhada: `shareds`

A lib `shareds` é um pacote **interno privado** hospedado no GitHub da organização `qbem-repos`. Ela fornece os blocos de construção reutilizáveis entre todos os serviços.

**Instalação via `pyproject.toml` (uv):**
```toml
[tool.uv.sources]
shareds = { git = "https://github.com/qbem-repos/dados-py-shareds.git", rev = "master" }
```

### Componentes utilizados

| Módulo `shareds`                                          | O que fornece                                                      |
|-----------------------------------------------------------|--------------------------------------------------------------------|
| `shareds.services.api_utils.jwt_token.JWTToken`           | Dependência FastAPI para validar JWT e extrair o usuário atual     |
| `shareds.services.app_security.user_scope.UserScope`      | Dataclass com perfil do usuário autenticado (id, email, módulos, superadmin, etc.) |
| `shareds.services.app_security.user_scope.security_check` | Decorator de autorização por módulo e perfil                       |
| `shareds.data_objects.exceptions.Exceptions`              | Exceções padronizadas que mapeiam para HTTP status codes           |
| `shareds.services.db_models_mixins.schema_generator.PydanticSchemaGeneratorMixin` | Mixin que adiciona `.to_pydantic_schema()` aos modelos SQLAlchemy |
| `shareds.config.getenv.SharedsGetEnv`                     | Base de configurações compartilhadas entre serviços                |

---

## 5. Segurança e Autenticação

### JWT Token

Todo endpoint usa `JWTToken.get_current_user` como dependência FastAPI. Ele valida o Bearer token na requisição e retorna um objeto `UserScope`.

```python
user_scope: UserScope = Depends(JWTToken.get_current_user)
```

### UserScope

Representa o contexto do usuário autenticado:

```python
@dataclass
class UserScope:
    user_id: int
    nome: str
    email: str
    corretora: ...
    estipulante: ...
    ativo: bool
    superadmin: bool
    perfil: ...
    modulos: list[str]   # ex: ["eb_backoffice"]
    categoria: ...
```

### `@security_check` decorator

Aplicado em **todos os métodos de service**, garante autorização antes de qualquer lógica:

```python
@security_check(
    "eb_backoffice",          # módulo que o usuário precisa ter acesso
    req_superadmin=True,      # exige que seja superadmin
    check_data_filters=False  # se deve aplicar filtros de dados por corretora/estipulante
)
async def create_rpa(data, user_scope, session, user_id=None):
    ...
```

---

## 6. Padrão de Service com Inner Classes

Este é o **padrão central** da arquitetura. Cada entidade possui uma classe `Service` com inner classes para cada operação CRUD + operações de BI.

```python
class EntidadeService:

    class Create:
        class Input(BaseModel):
            campo: str

        Output = Input  # ou EntidadeModel.to_pydantic_schema()
        # ou outra classe que herda BaseModel (pydantic)

        @staticmethod
        @security_check("modulo", req_superadmin=True, check_data_filters=False)
        async def create_entidade(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                obj = EntidadeModel(campo=data.campo)
                if user_id:
                    obj.created_by_user_id = user_id
                session.add(obj)
                await session.flush()
                await session.refresh(obj)
                await session.commit()
                return obj
            except IntegrityError as e:
                await session.rollback()
                if getattr(getattr(e, "orig", None), "pgcode", None) == "23505":
                    raise Exceptions.InUse("Entidade já cadastrada.")
                raise Exceptions.GenericError("Erro de integridade.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado: {err}")

    class Read:
        class Input(BaseModel):
            id: int  # ou nome: str para dimensões
        Output = Input  # ou EntidadeModel.to_pydantic_schema()

        @staticmethod
        @security_check(...)
        async def get_entidade(data: Input, user_scope: UserScope, session: AsyncSession):
            result = await session.execute(select(EntidadeModel).where(EntidadeModel.id == data.id))
            obj = result.scalar_one_or_none()
            if not obj:
                raise Exceptions.NotFound("Entidade não encontrada.")
            return obj

    class List:
        class Output(BaseModel):
            id: int
            nome: str

        @staticmethod
        @security_check(...)
        async def list_entidades(user_scope: UserScope, session: AsyncSession):
            result = await session.execute(select(EntidadeModel))
            return result.scalars().all()

    class Update:
        class Input(BaseModel):
            id: int
            novo_campo: str | None = None
        Output = EntidadeModel.to_pydantic_schema()

        @staticmethod
        @security_check(...)
        async def update_entidade(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            result = await session.execute(select(EntidadeModel).where(EntidadeModel.id == data.id))
            obj = result.scalar_one_or_none()
            if not obj:
                raise Exceptions.NotFound("Entidade não encontrada.")
            if user_id:
                obj.updated_by_user_id = user_id
            if data.novo_campo is not None:
                obj.campo = data.novo_campo
            await session.flush()
            await session.refresh(obj)
            await session.commit()
            return obj

    class Delete:
        class Input(BaseModel):
            id: int

        @staticmethod
        @security_check(...)
        async def delete_entidade(data: Input, user_scope: UserScope, session: AsyncSession):
            result = await session.execute(select(EntidadeModel).where(EntidadeModel.id == data.id))
            obj = result.scalar_one_or_none()
            if not obj:
                raise Exceptions.NotFound("Entidade não encontrada.")
            await session.delete(obj)
            await session.commit()

    class BI:
        """Operações analíticas para dashboards."""
        class ListTableInput(BaseModel):
            id: int | None = None
            nome: str | None = None

        @staticmethod
        @security_check(...)
        async def list_full_table(data: ListTableInput, user_scope: UserScope, session: AsyncSession):
            query = select(EntidadeModel)
            if data.id:
                query = query.where(EntidadeModel.id == data.id)
            result = await session.execute(query)
            return result.scalars().all()
```

**Regras deste padrão:**
- `Input` e `Output` são **sempre** Pydantic models definidos como inner classes.
- `Output` pode ser reutilizado como `Output = Input` quando entrada e saída têm os mesmos campos.
- `Output = EntidadeModel.to_pydantic_schema()` quando a saída deve refletir o schema completo do modelo.
- Todos os métodos são `@staticmethod` e `async`.
- O `session` é sempre passado como parâmetro (injeção — nunca criado dentro do service).
- `user_id` é passado como kwarg opcional para auditoria.

---

## 7. Padrão de Tratamento de Erros

Todos os services utilizam o padrão de exceções de `shareds.data_objects.exceptions.Exceptions`. Cada exceção mapeia para um HTTP status code no handler global:

| Exceção                          | HTTP Status | Quando usar                                         |
|----------------------------------|-------------|-----------------------------------------------------|
| `Exceptions.NotFound`            | 404         | Registro não encontrado no banco                    |
| `Exceptions.InUse`               | 409         | Violação de unicidade (pgcode `23505`)              |
| `Exceptions.DBConnectionError`   | 503         | `OperationalError` do SQLAlchemy                    |
| `Exceptions.GenericError`        | 500         | Qualquer exceção não prevista                       |

**Estrutura padrão do bloco try/except:**

```python
try:
    # lógica
except IntegrityError as e:
    await session.rollback()
    if getattr(getattr(e, "orig", None), "pgcode", None) == "23505":
        raise Exceptions.InUse("Mensagem específica.")
    raise Exceptions.GenericError("Erro de integridade.")
except OperationalError:
    await session.rollback()
    raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
except Exception as err:
    await session.rollback()
    raise Exceptions.GenericError(f"Erro inesperado: {err}")
```

---

## 8. Banco de Dados e Migrations (Alembic)

### Provisionamento inicial

Antes de rodar as migrations, o banco e o schema devem existir. O script `create_db_and_schemas.py` faz isso:

```bash
# Na raiz do projeto
python src/data/db_<nome>/create_db_and_schemas.py
```

### Configuração do Alembic

O Alembic é configurado **por banco de dados**, com os arquivos localizados em `src/data/db_<nome>/`:

- `alembic.ini` — config do Alembic (aponta `script_location = .`)
- `env.py` — conecta ao banco via `GetEnv`, importa `BaseModel.metadata` e todos os modelos via `_all_models`
- `versions/` — arquivos de revisão gerados

**Rodar migrations:**
```bash
cd src/data/db_<nome>
alembic upgrade head
```

**Gerar nova migration (autogenerate):**
```bash
cd src/data/db_<nome>
alembic revision --autogenerate -m "descricao da mudanca"
```

### Convenções de migration

- A **primeira migration** cria todas as tabelas do schema.
- **Migrations de seed** podem ser criadas para popular tabelas de dimensão com dados iniciais.
- Migrations de seed usam `op.execute(SQL)` com `ON CONFLICT DO NOTHING` para idempotência.
- O `env.py` sempre passa `include_schemas=True` para o Alembic gerenciar múltiplos schemas.

### `_all_models.py`

Re-exporta todos os modelos para garantir que o Alembic os descubra via `BaseModel.metadata`:

```python
# models/_all_models.py
from src.data.db_<nome>.models.<dominio> import *
```

---

## 9. Testes

### Estrutura

```
tests/
├── conftest.py          # Fixtures globais: db_session, user_scope
├── _tests_config.py     # Helpers e factories de dados de teste
└── application/
    └── <dominio>/
        └── test_<entidade>.py
```

### Fixtures (`conftest.py`)

```python
@pytest_asyncio.fixture
async def db_session():
    # Conecta ao banco de teste, cria o schema se necessário
    # Pula o teste se o banco não estiver disponível
    async with test_session_maker() as session:
        yield session

@pytest.fixture
def user_scope():
    return build_superadmin_scope()
```

### Helpers (`_tests_config.py`)

- `build_superadmin_scope()` — cria um `UserScope` de superadmin para os testes.
- `make_nome(prefix)` — gera nomes únicos usando UUID para evitar conflitos.
- `create_<entidade>(session)` — factories assíncronas que criam registros diretamente no banco.
- `cleanup_<entidade>(session, model)` — remove registros criados durante os testes.

### Padrão de teste

```python
@pytest.mark.asyncio
async def test_create_entidade_success(db_session, user_scope):
    data = EntidadeService.Create.Input(nome=make_nome("entidade"))
    model = await EntidadeService.Create.create_entidade(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(EntidadeService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_entidade(db_session, model.nome)  # limpeza garantida
```

**Regras de teste:**
- Testes **sempre** limpam os dados criados no `finally`.
- Testes verificam casos de sucesso **e** falha (ex: duplicata → `Exceptions.InUse` → `HTTPException 409`).
- O banco de teste é o mesmo banco real com prefixo de ambiente; o `conftest.py` pula automaticamente se o banco não estiver acessível.

---

## 10. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```dotenv
# Ambiente (dev, staging, prod)
ENVIRONMENT=dev

# Conexão PostgreSQL
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=sua_senha
```

O nome do banco será composto automaticamente: `<nome_db>_<ENVIRONMENT>` (ex: `backoffice_eb_dev`).

---

## 11. Dependências

### `pyproject.toml` (dependências diretas)

```toml
[project]
requires-python = ">=3.13"
dependencies = [
    "alembic>=1.18.4",
    "psycopg2>=2.9.11",
    "shareds",           # lib interna (ver abaixo)
]

[tool.uv.sources]
shareds = { git = "https://github.com/qbem-repos/dados-py-shareds.git", rev = "master" }
```

### Dependências transitivas relevantes (de `requirements.txt`)

| Pacote             | Versão   | Finalidade                                       |
|--------------------|----------|--------------------------------------------------|
| `fastapi`          | 0.133.0  | Framework HTTP assíncrono                        |
| `sqlalchemy`       | 2.0.47   | ORM e acesso ao banco (sync + async)             |
| `alembic`          | 1.18.4   | Migrations de schema                             |
| `pydantic`         | 2.12.5   | Validação de dados (Input/Output models)         |
| `psycopg2`         | 2.9.11   | Driver PostgreSQL síncrono                       |
| `python-dotenv`    | 1.2.1    | Carregamento do `.env`                           |
| `python-jose`      | 3.5.0    | Processamento de JWT                             |
| `bcrypt`           | 5.0.0    | Hash de senhas                                   |
| `sqlalchemy-utils` | 0.42.1   | Utilitários SQLAlchemy (criação de banco)        |
| `starlette`        | 0.52.1   | Base do FastAPI                                  |
| `anyio`            | 4.12.1   | Runtime assíncrono                               |
| `shareds`          | (git)    | Lib interna com segurança, exceções e mixins     |

### Instalação

```bash
# Com uv (recomendado)
uv sync

# Com pip
pip install -r requirements.txt
```

---

## 12. Guia de Reprodução em Novo Serviço

Siga este checklist para criar um novo serviço seguindo a mesma arquitetura base:

### 1. Inicializar projeto

```bash
uv init nome-do-novo-servico
cd nome-do-novo-servico
```

Configurar `pyproject.toml` com `requires-python = ">=3.13"` e adicionar dependências.

### 2. Criar estrutura de pastas

```
config/
  getenv.py
  getenv_mixins/
    db_postgres_connection.py   ← copiar do projeto base
    validate_env.py             ← copiar do projeto base
src/
  api_rest/
    main.py
    v1/
      main.py
      endpoints/
  application/
    <dominio>/
  data/
    db_<nome>/
      models/
        _base_model.py          ← copiar do projeto base
        _all_models.py
      db_session.py             ← copiar e adaptar
      create_db_and_schemas.py  ← copiar e adaptar
      alembic.ini               ← copiar do projeto base
      env.py                    ← copiar e adaptar
tests/
  conftest.py                   ← copiar e adaptar
  _tests_config.py
```

### 3. Configurar `GetEnv`

Em `config/getenv.py`, criar uma inner class por banco:

```python
class GetEnv(ValidateEnvMixin, SharedsGetEnv):
    class DB_NomeServico(_PostgresConnection):
        DB: str = "nome_servico_" + os.getenv("ENVIRONMENT")
```

### 4. Criar os modelos SQLAlchemy

Para cada domínio, em `src/data/db_<nome>/models/<dominio>.py`:

- Importar `BaseModel` de `models/_base_model.py`
- Criar tabelas de **dimensão** com `nome: str` como PK
- Criar tabelas de **entidade** com `id: int` como PK e FKs para dimensões
- Registrar todos em `_all_models.py`

### 5. Provisionar banco e rodar migrations

```bash
# 1. Criar banco e schema
python src/data/db_<nome>/create_db_and_schemas.py

# 2. Gerar migration inicial
cd src/data/db_<nome>
alembic revision --autogenerate -m "modelo inicial"

# 3. Aplicar
alembic upgrade head

# 4. (opcional) Criar migration de seed
alembic revision -m "seed dimensoes"
# editar o arquivo gerado com op.execute(SQL)
alembic upgrade head
```

### 6. Criar os Services

Para cada entidade em `src/application/<dominio>/<entidade>.py`:

- Seguir o padrão de inner classes (`Create`, `Read`, `List`, `Update`, `Delete`, `BI`)
- Sempre usar `@security_check` com o módulo correto
- Sempre passar `session` como parâmetro
- Sempre tratar `IntegrityError`, `OperationalError` e `Exception` genérico

### 7. Criar os Endpoints

Para cada recurso em `src/api_rest/v1/endpoints/<recurso>.py`:

- Criar `router = APIRouter(tags=[...], prefix="/...")`
- Usar `Depends(JWTToken.get_current_user)` e `Depends(get_async_db_session_dependency)` em todos os endpoints
- Usar a função `_to_output(model, output_cls)` para serializar a resposta
- Registrar o router em `src/api_rest/v1/main.py`

### 8. Configurar testes

- Copiar `tests/conftest.py` e adaptar para o novo banco
- Criar `tests/_tests_config.py` com `build_superadmin_scope()` e factories
- Criar testes para cada operação CRUD, incluindo casos de falha

### 9. Variáveis de ambiente

Criar `.env` na raiz com:
```
ENVIRONMENT=dev
POSTGRES_HOST=...
POSTGRES_PORT=5432
POSTGRES_USER=...
POSTGRES_PASSWORD=...
```

---

*Documento gerado em 04/03/2026. Atualizar conforme a arquitetura evolua.*
