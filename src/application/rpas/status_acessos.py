import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class StatusAcessosService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_status_acessos(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                status_acessos = StatusAcessosModel(nome=data.nome)
                if user_id is not None:
                    status_acessos.created_by_user_id = user_id

                session.add(status_acessos)
                await session.flush()
                await session.refresh(status_acessos)
                await session.commit()
                return status_acessos
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Status de acessos já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar status de acessos.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar status de acessos: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_status_acessos(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(StatusAcessosModel).where(StatusAcessosModel.nome == data.nome)
                )
                status_acessos = result.scalar_one_or_none()
                if not status_acessos:
                    raise Exceptions.NotFound("Status de acessos não encontrado.")
                return status_acessos
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar status de acessos: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_status_acessos(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(StatusAcessosModel)
                if data.nome:
                    query = query.where(StatusAcessosModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar status de acessos: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = StatusAcessosModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_status_acessos(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(StatusAcessosModel).where(StatusAcessosModel.nome == data.nome_atual)
                )
                status_acessos = result.scalar_one_or_none()
                if not status_acessos:
                    raise Exceptions.NotFound("Status de acessos não encontrado.")

                if user_id is not None:
                    status_acessos.updated_by_user_id = user_id

                status_acessos.nome = data.novo_nome
                await session.flush()
                await session.refresh(status_acessos)
                await session.commit()
                return status_acessos
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Status de acessos já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar status de acessos.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar status de acessos: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_status_acessos(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(StatusAcessosModel).where(StatusAcessosModel.nome == data.nome)
                )
                status_acessos = result.scalar_one_or_none()
                if not status_acessos:
                    raise Exceptions.NotFound("Status de acessos não encontrado.")

                await session.delete(status_acessos)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar status de acessos: {err}")
