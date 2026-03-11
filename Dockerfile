FROM python:3.13-slim

WORKDIR /app

# Dependências do sistema necessárias para psycopg2 e git (shareds via wheel local)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia wheels locais (pacotes privados) e requirements
COPY wheels/ ./wheels/
COPY requirements.txt .

# Instala dependências filtrando a linha editável local e a entrada do shareds (instalado via wheel local)
RUN grep -v "^-e" requirements.txt | grep -v "^#" | grep -v "^shareds" > /tmp/requirements_filtered.txt \
    && pip install --no-cache-dir -r /tmp/requirements_filtered.txt \
    && pip install --no-cache-dir wheels/shareds-0.1.0-py3-none-any.whl

# Copia o restante do projeto
COPY . .

# Instala o próprio pacote
RUN pip install --no-cache-dir .

EXPOSE 8000

CMD ["python", "main.py"]
