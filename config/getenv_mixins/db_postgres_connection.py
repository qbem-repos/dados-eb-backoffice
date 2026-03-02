import os
from dotenv import load_dotenv
load_dotenv()

class _PostgresConnection:
    DB: str = None
    HOST: str = os.getenv("POSTGRES_HOST")
    PORT: int = os.getenv("POSTGRES_PORT")
    USERNAME: str = os.getenv("POSTGRES_USER")
    PASSWORD: str = os.getenv("POSTGRES_PASSWORD")

    @classmethod
    def get_async_db_url(cls) -> str:
        return "postgresql+asyncpg://" + cls.USERNAME + ":" + cls.PASSWORD + "@" + cls.HOST + "/" + cls.DB

    @classmethod
    def get_sync_db_url(cls) -> str:
        return "postgresql+psycopg2://" + cls.USERNAME + ":" + cls.PASSWORD + "@" + cls.HOST + "/" + cls.DB
