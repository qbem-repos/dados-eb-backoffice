import sys
import pathlib

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from config.getenv import GetEnv
from tests._tests_config import build_superadmin_scope


test_async_engine = create_async_engine(
    GetEnv.DB_BackofficeEB.get_async_db_url(),
    poolclass=NullPool,
    echo=False,
)


test_session_maker = async_sessionmaker(
    test_async_engine,
    autoflush=True,
    expire_on_commit=False,
)


async def _ensure_db_available() -> None:
    if not all(
        [
            GetEnv.DB_BackofficeEB.HOST,
            GetEnv.DB_BackofficeEB.USERNAME,
            GetEnv.DB_BackofficeEB.PASSWORD,
            GetEnv.DB_BackofficeEB.DB,
        ]
    ):
        pytest.skip("Database not configured for tests. Set POSTGRES_* and ENVIRONMENT.")

    try:
        async with test_async_engine.connect() as conn:
            await conn.execute(text("CREATE SCHEMA IF NOT EXISTS rpas"))
            await conn.execute(text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"Database unavailable for tests: {exc}")


@pytest_asyncio.fixture
async def db_session():
    await _ensure_db_available()
    async with test_session_maker() as session:
        yield session


@pytest.fixture
def user_scope():
    return build_superadmin_scope()
