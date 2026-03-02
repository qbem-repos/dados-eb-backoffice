import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select

from pydantic import BaseModel

class TipoRPAService:
    class Create:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_tipo_rpa(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                tipo_rpa = TipoRPAModel(nome=data.nome)
                if user_id is not None:
                    tipo_rpa.created_by_user_id = user_id

                session.add(tipo_rpa)
                await session.flush()
                await session.refresh(tipo_rpa)
                await session.commit()
                return tipo_rpa
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Tipo de RPA já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar tipo de RPA.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar tipo de RPA: {err}")

    class Read:
        class Input(BaseModel):
            nome: str
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_tipo_rpa(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(TipoRPAModel).where(TipoRPAModel.nome == data.nome)
                )
                tipo_rpa = result.scalar_one_or_none()
                if not tipo_rpa:
                    raise Exceptions.NotFound("Tipo de RPA não encontrado.")
                return tipo_rpa
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar tipo de RPA: {err}")

    class List:
        class Input(BaseModel):
            nome: str | None = None
        Output = list[Input]

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_tipos_rpa(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(TipoRPAModel)
                if data.nome:
                    query = query.where(TipoRPAModel.nome.ilike(f"%{data.nome}%"))
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar tipos de RPA: {err}")

    class Update:
        class Input(BaseModel):
            nome_atual: str
            novo_nome: str
        Output = TipoRPAModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_tipo_rpa(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                result = await session.execute(
                    select(TipoRPAModel).where(TipoRPAModel.nome == data.nome_atual)
                )
                tipo_rpa = result.scalar_one_or_none()
                if not tipo_rpa:
                    raise Exceptions.NotFound("Tipo de RPA não encontrado.")

                if user_id is not None:
                    tipo_rpa.updated_by_user_id = user_id

                tipo_rpa.nome = data.novo_nome
                await session.flush()
                await session.refresh(tipo_rpa)
                await session.commit()
                return tipo_rpa
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("Tipo de RPA já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar tipo de RPA.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar tipo de RPA: {err}")

    class Delete:
        class Input(BaseModel):
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_tipo_rpa(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(TipoRPAModel).where(TipoRPAModel.nome == data.nome)
                )
                tipo_rpa = result.scalar_one_or_none()
                if not tipo_rpa:
                    raise Exceptions.NotFound("Tipo de RPA não encontrado.")

                await session.delete(tipo_rpa)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar tipo de RPA: {err}")
