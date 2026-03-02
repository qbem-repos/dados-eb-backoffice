import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from sqlalchemy.orm import declarative_base

from sqlalchemy import DateTime, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from pydantic import BaseModel as PydanticBaseModel

from shareds.services.db_models_mixins.schema_generator import PydanticSchemaGeneratorMixin

_Base = declarative_base()

class BaseModel(_Base, PydanticSchemaGeneratorMixin):
    __abstract__ = True
    __table_args__ = {"schema": "rpas"}

    created_at: Mapped[datetime]= mapped_column(DateTime, default=datetime.now(), nullable=True)
    created_by_user_id: Mapped[int] = mapped_column(Integer, nullable=True)
    updated_at: Mapped[datetime]= mapped_column(DateTime, nullable=True)
    updated_by_user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    @classmethod
    def AUDIT_FIELDS(cls) -> list:
        return ["created_at", "created_by_user_id", "updated_at", "updated_by_user_id"]

    async def create_and_get_id(self, session: AsyncSession, user_id: int = None) -> int:
        try:
            if user_id is not None:
                self.created_by_user_id = user_id

            session.add(self)
            await session.flush()
            await session.refresh(self)            
            await session.commit()            
            return self.id            
        except Exception as e:
            await session.rollback()
            print(f"Erro ao adicionar {self.__class__.__name__}: {e}")

    async def update(self, user_id: int, values: dict, session: AsyncSession
                     , blocked_fields: list = []) -> int:
        default_blocked_fields = ["id", "created_at", "created_by_user_id"]
        blocked_fields = blocked_fields + default_blocked_fields
        try:
            values["updated_at"] = datetime.now()
            values["updated_by_user_id"] = user_id
            for key, value in values.items():
                if key in blocked_fields:
                    continue
                setattr(self, key, value)
            await session.flush()
            await session.refresh(self)
            await session.commit()
            return self
        except Exception as e:
            await session.rollback()
            print(f"Erro ao atualizar {self.__class__.__name__}: {e}")

    async def delete(self, session: AsyncSession) -> None:
        try:
            await session.delete(self)
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Erro ao deletar {self.__class__.__name__}: {e}")
