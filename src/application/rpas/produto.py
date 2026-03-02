import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class ProdutoService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_produto(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                produto = ProdutoModel(nome=data.nome)
                if user_id is not None:
                    produto.created_by_user_id = user_id

                session.add(produto)
                await session.flush()
                await session.refresh(produto)
                await session.commit()
                return produto
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Produto já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar produto.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar produto: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_produto(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(ProdutoModel).where(ProdutoModel.nome == data.nome)
                )
                produto = result.scalar_one_or_none()
                if not produto:
                    raise Exceptions.NotFound("Produto não encontrado.")
                return produto
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar produto: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_produtos(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(ProdutoModel)
                if data.nome:
                    query = query.where(ProdutoModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar produtos: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = ProdutoModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_produto(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(ProdutoModel).where(ProdutoModel.nome == data.nome_atual)
                )
                produto = result.scalar_one_or_none()
                if not produto:
                    raise Exceptions.NotFound("Produto não encontrado.")

                if user_id is not None:
                    produto.updated_by_user_id = user_id

                produto.nome = data.novo_nome
                await session.flush()
                await session.refresh(produto)
                await session.commit()
                return produto
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Produto já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar produto.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar produto: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_produto(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(ProdutoModel).where(ProdutoModel.nome == data.nome)
                )
                produto = result.scalar_one_or_none()
                if not produto:
                    raise Exceptions.NotFound("Produto não encontrado.")

                await session.delete(produto)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar produto: {err}")
