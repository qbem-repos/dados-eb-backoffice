import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class TipoContratoService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_tipo_contrato(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                tipo_contrato = TipoContratoModel(nome=data.nome)
                if user_id is not None:
                    tipo_contrato.created_by_user_id = user_id

                session.add(tipo_contrato)
                await session.flush()
                await session.refresh(tipo_contrato)
                await session.commit()
                return tipo_contrato
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Tipo de contrato já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar tipo de contrato.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar tipo de contrato: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_tipo_contrato(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(TipoContratoModel).where(TipoContratoModel.nome == data.nome)
                )
                tipo_contrato = result.scalar_one_or_none()
                if not tipo_contrato:
                    raise Exceptions.NotFound("Tipo de contrato não encontrado.")
                return tipo_contrato
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar tipo de contrato: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_tipos_contrato(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(TipoContratoModel)
                if data.nome:
                    query = query.where(TipoContratoModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar tipos de contrato: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = TipoContratoModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_tipo_contrato(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(TipoContratoModel).where(TipoContratoModel.nome == data.nome_atual)
                )
                tipo_contrato = result.scalar_one_or_none()
                if not tipo_contrato:
                    raise Exceptions.NotFound("Tipo de contrato não encontrado.")

                if user_id is not None:
                    tipo_contrato.updated_by_user_id = user_id

                tipo_contrato.nome = data.novo_nome
                await session.flush()
                await session.refresh(tipo_contrato)
                await session.commit()
                return tipo_contrato
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Tipo de contrato já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar tipo de contrato.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar tipo de contrato: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_tipo_contrato(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(TipoContratoModel).where(TipoContratoModel.nome == data.nome)
                )
                tipo_contrato = result.scalar_one_or_none()
                if not tipo_contrato:
                    raise Exceptions.NotFound("Tipo de contrato não encontrado.")

                await session.delete(tipo_contrato)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar tipo de contrato: {err}")
