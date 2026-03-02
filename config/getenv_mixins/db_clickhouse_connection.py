import os
from dotenv import load_dotenv
load_dotenv()

class _ClickhouseConnection:
    DB: str = None
    HOST: str = os.getenv("CLICKHOUSE_HOST")
    PORT: int = os.getenv("CLICKHOUSE_PORT")
    USERNAME: str = os.getenv("CLICKHOUSE_USERNAME")
    PASSWORD: str = os.getenv("CLICKHOUSE_PASSWORD")

    @classmethod
    def get_db_url(cls) -> str:
        return "clickhouse://" + cls.USERNAME + ":" + cls.PASSWORD + "@" + cls.HOST + "/" + cls.DB