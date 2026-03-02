import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class StatusService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_status(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                status = StatusModel(nome=data.nome)
                if user_id is not None:
                    status.created_by_user_id = user_id

                session.add(status)
                await session.flush()
                await session.refresh(status)
                await session.commit()
                return status
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Status já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar status.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar status: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_status(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(StatusModel).where(StatusModel.nome == data.nome)
                )
                status = result.scalar_one_or_none()
                if not status:
                    raise Exceptions.NotFound("Status não encontrado.")
                return status
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar status: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_status(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(StatusModel)
                if data.nome:
                    query = query.where(StatusModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar status: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = StatusModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_status(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(StatusModel).where(StatusModel.nome == data.nome_atual)
                )
                status = result.scalar_one_or_none()
                if not status:
                    raise Exceptions.NotFound("Status não encontrado.")

                if user_id is not None:
                    status.updated_by_user_id = user_id

                status.nome = data.novo_nome
                await session.flush()
                await session.refresh(status)
                await session.commit()
                return status
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Status já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar status.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar status: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_status(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(StatusModel).where(StatusModel.nome == data.nome)
                )
                status = result.scalar_one_or_none()
                if not status:
                    raise Exceptions.NotFound("Status não encontrado.")

                await session.delete(status)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar status: {err}")
