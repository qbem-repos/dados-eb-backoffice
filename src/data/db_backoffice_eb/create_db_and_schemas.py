import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from config.getenv import GetEnv

from sqlalchemy import create_engine, text
from sqlalchemy_utils import database_exists, create_database


def get_engine():
    """Retorna a engine do banco de dados configurada."""
    db_url = GetEnv.DB_BackofficeEB.get_sync_db_url()
    return create_engine(db_url, connect_args={'client_encoding': 'utf8'})

def create_db_if_not_exists():
    """
    Verifica se o banco de dados existe. Se não, o cria.
    """
    engine = get_engine()
    db_name = GetEnv.DB_BackofficeEB.DB

    print(engine.url)
    
    print(f"Verificando existência do banco de dados '{db_name}'...")
    try:
        if not database_exists(engine.url):
            print(f"Banco de dados '{db_name}' não encontrado. Criando...")
            create_database(engine.url)
            print(f"Banco de dados '{db_name}' criado com sucesso.")
        else:
            print(f"Banco de dados '{db_name}' já existe.")
    except Exception as e:
        print(f"ERRO ao verificar/criar banco de dados: {e}")
        sys.exit(1)


def create_schema_if_not_exists(schema_name: str = "rpas"):
    """
    Verifica se o schema existe. Se não, o cria.
    """
    engine = get_engine()
    try:
        with engine.begin() as connection:
            connection.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
        print(f"Schema '{schema_name}' pronto para uso.")
    except Exception as e:
        print(f"ERRO ao verificar/criar schema '{schema_name}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("--- Iniciando processo de configuração do banco de dados ---")
    
    # 1. Cria o banco se não existir
    create_db_if_not_exists()

    # 2. Cria o schema se não existir
    create_schema_if_not_exists("rpas")
    
    print("--- Processo concluído ---")