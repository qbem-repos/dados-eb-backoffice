import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models.rpas import *
from shareds.data_objects.exceptions import Exceptions
from shareds.services.app_security.user_scope import UserScope, security_check
from sqlalchemy.exc import IntegrityError, OperationalError
from sqlalchemy import select, func

from pydantic import BaseModel
from datetime import datetime

class RPAService:
    class Create:
        class Input(BaseModel):
            nome: str
            operadora_nome: str
            produto_nome: str
            tipo_contrato_nome: str
            processo_nome: str
            tipo_rpa_nome: str
            status_nome: str
            status_detalhe: str | None = None
            status_last_update: datetime | None = None
            retencao_carteirinha_nome: str
            doc_baixa: str | None = None
            forma_operacao_nome: str
            status_acesso_nome: str
            status_acesso_detalhe: str | None = None
            status_acesso_last_update: datetime | None = None
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def create_rpa(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                rpa = RPAModel(
                    nome=data.nome,
                    operadora_nome=data.operadora_nome,
                    produto_nome=data.produto_nome,
                    tipo_contrato_nome=data.tipo_contrato_nome,
                    processo_nome=data.processo_nome,
                    tipo_rpa_nome=data.tipo_rpa_nome,
                    status_nome=data.status_nome,
                    status_detalhe=data.status_detalhe,
                    status_last_update=data.status_last_update,
                    retencao_carteirinha_nome=data.retencao_carteirinha_nome,
                    doc_baixa=data.doc_baixa,
                    forma_operacao_nome=data.forma_operacao_nome,
                    status_acesso_nome=data.status_acesso_nome,
                    status_acesso_detalhe=data.status_acesso_detalhe,
                    status_acesso_last_update=data.status_acesso_last_update,
                )
                if user_id is not None:
                    rpa.created_by_user_id = user_id

                session.add(rpa)
                await session.flush()
                await session.refresh(rpa)
                await session.commit()
                return rpa
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("RPA já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao cadastrar RPA.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao cadastrar RPA: {err}")

    class Read:
        class Input(BaseModel):
            id: int
        Output = Input

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def get_rpa(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(RPAModel).where(RPAModel.id == data.id)
                )
                rpa = result.scalar_one_or_none()
                if not rpa:
                    raise Exceptions.NotFound("RPA não encontrado.")
                return rpa
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao buscar RPA: {err}")

    class List:
        class Output(BaseModel):
            id: int
            nome: str

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_rpas(user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(select(RPAModel.id, RPAModel.nome))
                return [RPAService.List.Output(id=row[0], nome=row[1]) for row in result.all()]
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar RPAs: {err}")

    class Update:
        class Input(BaseModel):
            id: int
            novo_nome: str | None = None
            operadora_nome: str | None = None
            produto_nome: str | None = None
            tipo_contrato_nome: str | None = None
            processo_nome: str | None = None
            tipo_rpa_nome: str | None = None
            status_nome: str | None = None
            status_detalhe: str | None = None
            status_last_update: datetime | None = None
            retencao_carteirinha_nome: str | None = None
            doc_baixa: str | None = None
            forma_operacao_nome: str | None = None
            status_acesso_nome: str | None = None
            status_acesso_detalhe: str | None = None
            status_acesso_last_update: datetime | None = None
        Output = RPAModel.to_pydantic_schema()

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def update_rpa(data: Input, user_scope: UserScope, session: AsyncSession, user_id: int = None):
            try:
                query = select(RPAModel).where(RPAModel.id == data.id)
                result = await session.execute(query)
                rpa = result.scalar_one_or_none()
                if not rpa:
                    raise Exceptions.NotFound("RPA não encontrado.")

                if user_id is not None:
                    rpa.updated_by_user_id = user_id

                if data.novo_nome is not None:
                    rpa.nome = data.novo_nome
                if data.operadora_nome is not None:
                    rpa.operadora_nome = data.operadora_nome
                if data.produto_nome is not None:
                    rpa.produto_nome = data.produto_nome
                if data.tipo_contrato_nome is not None:
                    rpa.tipo_contrato_nome = data.tipo_contrato_nome
                if data.processo_nome is not None:
                    rpa.processo_nome = data.processo_nome
                if data.tipo_rpa_nome is not None:
                    rpa.tipo_rpa_nome = data.tipo_rpa_nome
                if data.status_nome is not None:
                    rpa.status_nome = data.status_nome
                if data.status_detalhe is not None:
                    rpa.status_detalhe = data.status_detalhe
                if data.status_last_update is not None:
                    rpa.status_last_update = data.status_last_update
                if data.retencao_carteirinha_nome is not None:
                    rpa.retencao_carteirinha_nome = data.retencao_carteirinha_nome
                if data.doc_baixa is not None:
                    rpa.doc_baixa = data.doc_baixa
                if data.forma_operacao_nome is not None:
                    rpa.forma_operacao_nome = data.forma_operacao_nome
                if data.status_acesso_nome is not None:
                    rpa.status_acesso_nome = data.status_acesso_nome
                if data.status_acesso_detalhe is not None:
                    rpa.status_acesso_detalhe = data.status_acesso_detalhe
                if data.status_acesso_last_update is not None:
                    rpa.status_acesso_last_update = data.status_acesso_last_update

                await session.flush()
                await session.refresh(rpa)
                await session.commit()
                return rpa
            except IntegrityError as e:
                await session.rollback()
                pgcode = getattr(getattr(e, "orig", None), "pgcode", None)
                if pgcode == "23505":
                    raise Exceptions.InUse("RPA já cadastrado.")
                raise Exceptions.GenericError("Erro de integridade ao atualizar RPA.")
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao atualizar RPA: {err}")

    class Delete:
        class Input(BaseModel):
            id: int

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def delete_rpa(data: Input, user_scope: UserScope, session: AsyncSession):
            try:
                query = select(RPAModel).where(RPAModel.id == data.id)
                result = await session.execute(query)
                rpa = result.scalar_one_or_none()
                if not rpa:
                    raise Exceptions.NotFound("RPA não encontrado.")

                await session.delete(rpa)
                await session.commit()
            except OperationalError:
                await session.rollback()
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                await session.rollback()
                raise Exceptions.GenericError(f"Erro inesperado ao deletar RPA: {err}")

    class BI:

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def list_full_table(user_scope: UserScope, session: AsyncSession):
            try:
                query = select(RPAModel)
                result = await session.execute(query)
                return result.scalars().all()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao listar RPAs: {err}")

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def total_rpas(user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(select(func.count(RPAModel.id)))
                return result.scalar_one()
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao contar RPAs: {err}")

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def total_por_status(user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(RPAModel.status_nome, func.count(RPAModel.id)).group_by(RPAModel.status_nome)
                )
                return {row[0]: row[1] for row in result.all()}
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao contar RPAs por status: {err}")

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def total_por_status_acesso(user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(RPAModel.status_acesso_nome, func.count(RPAModel.id)).group_by(RPAModel.status_acesso_nome)
                )
                return [{"status_acesso_nome": row[0], "total": row[1]} for row in result.all()]
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao contar RPAs por status de acesso: {err}")

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def total_por_produto(user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(RPAModel.produto_nome, func.count(RPAModel.id)).group_by(RPAModel.produto_nome)
                )
                return [{"produto_nome": row[0], "total": row[1]} for row in result.all()]
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao contar RPAs por produto: {err}")

        @staticmethod
        @security_check("eb_backoffice", req_superadmin=True, check_data_filters=False)
        async def total_por_processo(user_scope: UserScope, session: AsyncSession):
            try:
                result = await session.execute(
                    select(RPAModel.processo_nome, func.count(RPAModel.id)).group_by(RPAModel.processo_nome)
                )
                return [{"processo_nome": row[0], "total": row[1]} for row in result.all()]
            except OperationalError:
                raise Exceptions.DBConnectionError("Erro de conexão com a base de dados.")
            except Exception as err:
                raise Exceptions.GenericError(f"Erro inesperado ao contar RPAs por processo: {err}")
