import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class ProcessoService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_processo(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                processo = ProcessoModel(nome=data.nome)
                if user_id is not None:
                    processo.created_by_user_id = user_id

                session.add(processo)
                await session.flush()
                await session.refresh(processo)
                await session.commit()
                return processo
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Processo já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar processo.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar processo: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_processo(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(ProcessoModel).where(ProcessoModel.nome == data.nome)
                )
                processo = result.scalar_one_or_none()
                if not processo:
                    raise Exceptions.NotFound("Processo não encontrado.")
                return processo
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar processo: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_processos(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(ProcessoModel)
                if data.nome:
                    query = query.where(ProcessoModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar processos: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = ProcessoModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_processo(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(ProcessoModel).where(ProcessoModel.nome == data.nome_atual)
                )
                processo = result.scalar_one_or_none()
                if not processo:
                    raise Exceptions.NotFound("Processo não encontrado.")

                if user_id is not None:
                    processo.updated_by_user_id = user_id

                processo.nome = data.novo_nome
                await session.flush()
                await session.refresh(processo)
                await session.commit()
                return processo
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Processo já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar processo.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar processo: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_processo(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(ProcessoModel).where(ProcessoModel.nome == data.nome)
                )
                processo = result.scalar_one_or_none()
                if not processo:
                    raise Exceptions.NotFound("Processo não encontrado.")

                await session.delete(processo)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar processo: {err}")
