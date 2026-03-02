import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class FormaOperacaoService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_forma_operacao(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                forma_operacao = FormaOperacaoModel(nome=data.nome)
                if user_id is not None:
                    forma_operacao.created_by_user_id = user_id

                session.add(forma_operacao)
                await session.flush()
                await session.refresh(forma_operacao)
                await session.commit()
                return forma_operacao
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Forma de operação já cadastrada.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar forma de operação.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar forma de operação: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_forma_operacao(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(FormaOperacaoModel).where(FormaOperacaoModel.nome == data.nome)
                )
                forma_operacao = result.scalar_one_or_none()
                if not forma_operacao:
                    raise Exceptions.NotFound("Forma de operação não encontrada.")
                return forma_operacao
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar forma de operação: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_formas_operacao(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(FormaOperacaoModel)
                if data.nome:
                    query = query.where(FormaOperacaoModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar formas de operação: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = FormaOperacaoModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_forma_operacao(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(FormaOperacaoModel).where(FormaOperacaoModel.nome == data.nome_atual)
                )
                forma_operacao = result.scalar_one_or_none()
                if not forma_operacao:
                    raise Exceptions.NotFound("Forma de operação não encontrada.")

                if user_id is not None:
                    forma_operacao.updated_by_user_id = user_id

                forma_operacao.nome = data.novo_nome
                await session.flush()
                await session.refresh(forma_operacao)
                await session.commit()
                return forma_operacao
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Forma de operação já cadastrada.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar forma de operação.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar forma de operação: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_forma_operacao(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(FormaOperacaoModel).where(FormaOperacaoModel.nome == data.nome)
                )
                forma_operacao = result.scalar_one_or_none()
                if not forma_operacao:
                    raise Exceptions.NotFound("Forma de operação não encontrada.")

                await session.delete(forma_operacao)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar forma de operação: {err}")
