import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("config")[0])

import os
from dotenv import load_dotenv
load_dotenv()

from config.getenv_mixins.db_postgres_connection import _PostgresConnection
from config.getenv_mixins.validate_env import ValidateEnvMixin

from shareds.config.getenv import SharedsGetEnv

class GetEnv(ValidateEnvMixin
             , SharedsGetEnv):

    class DB_BackofficeEB(_PostgresConnection):
        DB: str = "backoffice_eb_" + os.getenv("ENVIRONMENT")

if __name__ == "__main__":
    GetEnv.validate_all_env_vars()