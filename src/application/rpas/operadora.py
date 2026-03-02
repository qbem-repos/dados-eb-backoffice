import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError, SQLAlchemyError
from sqlalchemy import select

from pydantic import BaseModel

class OperadoraService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_operadora(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                operadora = OperadoraModel(nome=data.nome)
                if user_id is not None:
                    operadora.created_by_user_id = user_id

                session.add(operadora)
                await session.flush()
                await session.refresh(operadora)
                await session.commit()
                return operadora
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Operadora já cadastrada.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar operadora.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar operadora: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_operadora(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(OperadoraModel).where(OperadoraModel.nome == data.nome)
                )
                operadora = result.scalar_one_or_none()
                if not operadora:
                    raise Exceptions.NotFound("Operadora não encontrada.")
                return operadora
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar operadora: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_operadoras(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(OperadoraModel)
                if data.nome:
                    query = query.where(OperadoraModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar operadoras: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = OperadoraModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_operadora(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(OperadoraModel).where(OperadoraModel.nome == data.nome_atual)
                )
                operadora = result.scalar_one_or_none()
                if not operadora:
                    raise Exceptions.NotFound("Operadora não encontrada.")

                if user_id is not None:
                    operadora.updated_by_user_id = user_id

                operadora.nome = data.novo_nome
                await session.flush()
                await session.refresh(operadora)
                await session.commit()
                return operadora
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Operadora já cadastrada.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar operadora.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar operadora: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_operadora(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(OperadoraModel).where(OperadoraModel.nome == data.nome)
                )
                operadora = result.scalar_one_or_none()
                if not operadora:
                    raise Exceptions.NotFound("Operadora não encontrada.")

                await session.delete(operadora)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar operadora: {err}")