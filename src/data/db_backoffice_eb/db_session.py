import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from config.getenv import GetEnv

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.orm import sessionmaker

from contextlib import asynccontextmanager
from typing import AsyncGenerator

sync_engine = create_engine(GetEnv.DB_BackofficeEB.get_sync_db_url(), echo=False)
sync_session_maker = sessionmaker(bind=sync_engine)

async_engine = create_async_engine(GetEnv.DB_BackofficeEB.get_async_db_url(), echo=False)
async_session_maker = async_sessionmaker(async_engine, autoflush=True, expire_on_commit=False)

def get_session(is_async: bool = True):
    if is_async:
        return async_session_maker()
    else:
        return sync_session_maker()

@asynccontextmanager
async def get_managed_session(is_async: bool = True) -> AsyncGenerator[AsyncSession, None]:
    """
    Fornece uma sessão de DB que gerencia seu próprio ciclo de vida (commit/rollback/close).
    Deve ser usada com 'async with'.
    """
    session = get_session(is_async)
    try:
        yield session
        if is_async:
            await session.commit()
        else:
            session.commit()
    except Exception:
        if is_async:
            await session.rollback()
        else:
            session.rollback()
        raise
    finally:
        if session is not None:
            if is_async:
                await session.close()
            else:
                session.close()


async def get_async_db_session_dependency() -> AsyncGenerator[AsyncSession, None]:
    async with get_managed_session(is_async=True) as session:
        yield session