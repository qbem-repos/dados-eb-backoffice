import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class RetencaoCarteirinhaService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_retencao_carteirinha(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                retencao = RetencaoCarteirinhaModel(nome=data.nome)
                if user_id is not None:
                    retencao.created_by_user_id = user_id

                session.add(retencao)
                await session.flush()
                await session.refresh(retencao)
                await session.commit()
                return retencao
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Retenção de carteirinha já cadastrada.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar retenção de carteirinha.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar retenção de carteirinha: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_retencao_carteirinha(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(RetencaoCarteirinhaModel).where(RetencaoCarteirinhaModel.nome == data.nome)
                )
                retencao = result.scalar_one_or_none()
                if not retencao:
                    raise Exceptions.NotFound("Retenção de carteirinha não encontrada.")
                return retencao
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar retenção de carteirinha: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_retencoes_carteirinha(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(RetencaoCarteirinhaModel)
                if data.nome:
                    query = query.where(RetencaoCarteirinhaModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar retenções de carteirinha: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = RetencaoCarteirinhaModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_retencao_carteirinha(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(RetencaoCarteirinhaModel).where(RetencaoCarteirinhaModel.nome == data.nome_atual)
                )
                retencao = result.scalar_one_or_none()
                if not retencao:
                    raise Exceptions.NotFound("Retenção de carteirinha não encontrada.")

                if user_id is not None:
                    retencao.updated_by_user_id = user_id

                retencao.nome = data.novo_nome
                await session.flush()
                await session.refresh(retencao)
                await session.commit()
                return retencao
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Retenção de carteirinha já cadastrada.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar retenção de carteirinha.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar retenção de carteirinha: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_retencao_carteirinha(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(RetencaoCarteirinhaModel).where(RetencaoCarteirinhaModel.nome == data.nome)
                )
                retencao = result.scalar_one_or_none()
                if not retencao:
                    raise Exceptions.NotFound("Retenção de carteirinha não encontrada.")

                await session.delete(retencao)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar retenção de carteirinha: {err}")
