import sys
import pathlib
from dataclasses import dataclass
from typing import Optional, List
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(pathlib.Path(__file__)).split("tests")[0])

from src.data.db_backoffice_eb.models.rpas import (
    OperadoraModel,
    ProdutoModel,
    TipoContratoModel,
    ProcessoModel,
    TipoRPAModel,
    StatusModel,
    RetencaoCarteirinhaModel,
    FormaOperacaoModel,
    StatusAcessosModel,
    RPAModel,
)
from shareds.services.app_security.user_scope import UserScope


def make_nome(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def validate_output(output_model, result):
    return output_model.model_validate(result, from_attributes=True)


@dataclass
class BaseTestData:
    user_id: int
    email: str


def build_superadmin_scope(data: Optional[BaseTestData] = None, ativo: bool = True) -> UserScope:
    return UserScope(
        user_id=data.user_id if data else 1,
        nome="Admin Teste",
        email=data.email if data else "admin@test.local",
        corretora=None,
        estipulante=None,
        ativo=ativo,
        superadmin=True,
        perfil=None,
        modulos=["eb_backoffice"],
        categoria=None,
    )


async def create_operadora(session: AsyncSession, nome: Optional[str] = None) -> OperadoraModel:
    model = OperadoraModel(nome=nome or make_nome("operadora"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_operadora(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(OperadoraModel).where(OperadoraModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_produto(session: AsyncSession, nome: Optional[str] = None) -> ProdutoModel:
    model = ProdutoModel(nome=nome or make_nome("produto"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_produto(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(ProdutoModel).where(ProdutoModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_tipo_contrato(session: AsyncSession, nome: Optional[str] = None) -> TipoContratoModel:
    model = TipoContratoModel(nome=nome or make_nome("tipo_contrato"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_tipo_contrato(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(TipoContratoModel).where(TipoContratoModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_processo(session: AsyncSession, nome: Optional[str] = None) -> ProcessoModel:
    model = ProcessoModel(nome=nome or make_nome("processo"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_processo(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(ProcessoModel).where(ProcessoModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_tipo_rpa(session: AsyncSession, nome: Optional[str] = None) -> TipoRPAModel:
    model = TipoRPAModel(nome=nome or make_nome("tipo_rpa"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_tipo_rpa(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(TipoRPAModel).where(TipoRPAModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_status(session: AsyncSession, nome: Optional[str] = None) -> StatusModel:
    model = StatusModel(nome=nome or make_nome("status"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_status(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(StatusModel).where(StatusModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_retencao_carteirinha(session: AsyncSession, nome: Optional[str] = None) -> RetencaoCarteirinhaModel:
    model = RetencaoCarteirinhaModel(nome=nome or make_nome("retencao"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_retencao_carteirinha(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(RetencaoCarteirinhaModel).where(RetencaoCarteirinhaModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_forma_operacao(session: AsyncSession, nome: Optional[str] = None) -> FormaOperacaoModel:
    model = FormaOperacaoModel(nome=nome or make_nome("forma_operacao"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_forma_operacao(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(FormaOperacaoModel).where(FormaOperacaoModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_status_acessos(session: AsyncSession, nome: Optional[str] = None) -> StatusAcessosModel:
    model = StatusAcessosModel(nome=nome or make_nome("status_acessos"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_status_acessos(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(StatusAcessosModel).where(StatusAcessosModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


@dataclass
class RpaDependencies:
    operadora: OperadoraModel
    produto: ProdutoModel
    tipo_contrato: TipoContratoModel
    processo: ProcessoModel
    tipo_rpa: TipoRPAModel
    status: StatusModel
    retencao: RetencaoCarteirinhaModel
    forma_operacao: FormaOperacaoModel
    status_acessos: StatusAcessosModel


@dataclass
class RpaDependencyNames:
    operadora_nome: str
    produto_nome: str
    tipo_contrato_nome: str
    processo_nome: str
    tipo_rpa_nome: str
    status_nome: str
    retencao_nome: str
    forma_operacao_nome: str
    status_acessos_nome: str


async def create_rpa_dependencies(session: AsyncSession) -> RpaDependencies:
    operadora = await create_operadora(session)
    produto = await create_produto(session)
    tipo_contrato = await create_tipo_contrato(session)
    processo = await create_processo(session)
    tipo_rpa = await create_tipo_rpa(session)
    status = await create_status(session)
    retencao = await create_retencao_carteirinha(session)
    forma_operacao = await create_forma_operacao(session)
    status_acessos = await create_status_acessos(session)
    return RpaDependencies(
        operadora=operadora,
        produto=produto,
        tipo_contrato=tipo_contrato,
        processo=processo,
        tipo_rpa=tipo_rpa,
        status=status,
        retencao=retencao,
        forma_operacao=forma_operacao,
        status_acessos=status_acessos,
    )


async def cleanup_rpa_dependencies(session: AsyncSession, deps: RpaDependencies) -> None:
    await delete_status_acessos(session, deps.status_acessos.nome)
    await delete_forma_operacao(session, deps.forma_operacao.nome)
    await delete_retencao_carteirinha(session, deps.retencao.nome)
    await delete_status(session, deps.status.nome)
    await delete_tipo_rpa(session, deps.tipo_rpa.nome)
    await delete_processo(session, deps.processo.nome)
    await delete_tipo_contrato(session, deps.tipo_contrato.nome)
    await delete_produto(session, deps.produto.nome)
    await delete_operadora(session, deps.operadora.nome)


def snapshot_rpa_dependency_names(deps: RpaDependencies) -> RpaDependencyNames:
    return RpaDependencyNames(
        operadora_nome=deps.operadora.nome,
        produto_nome=deps.produto.nome,
        tipo_contrato_nome=deps.tipo_contrato.nome,
        processo_nome=deps.processo.nome,
        tipo_rpa_nome=deps.tipo_rpa.nome,
        status_nome=deps.status.nome,
        retencao_nome=deps.retencao.nome,
        forma_operacao_nome=deps.forma_operacao.nome,
        status_acessos_nome=deps.status_acessos.nome,
    )


async def cleanup_rpa_dependencies_by_names(session: AsyncSession, names: RpaDependencyNames) -> None:
    await delete_status_acessos(session, names.status_acessos_nome)
    await delete_forma_operacao(session, names.forma_operacao_nome)
    await delete_retencao_carteirinha(session, names.retencao_nome)
    await delete_status(session, names.status_nome)
    await delete_tipo_rpa(session, names.tipo_rpa_nome)
    await delete_processo(session, names.processo_nome)
    await delete_tipo_contrato(session, names.tipo_contrato_nome)
    await delete_produto(session, names.produto_nome)
    await delete_operadora(session, names.operadora_nome)


async def create_rpa(session: AsyncSession, deps: Optional[RpaDependencies] = None, nome: Optional[str] = None) -> tuple[RPAModel, RpaDependencies]:
    deps = deps or await create_rpa_dependencies(session)
    model = RPAModel(
        nome=nome or make_nome("rpa"),
        operadora_nome=deps.operadora.nome,
        produto_nome=deps.produto.nome,
        tipo_contrato_nome=deps.tipo_contrato.nome,
        processo_nome=deps.processo.nome,
        tipo_rpa_nome=deps.tipo_rpa.nome,
        status_nome=deps.status.nome,
        retencao_carteirinha_nome=deps.retencao.nome,
        doc_baixa=None,
        forma_operacao_nome=deps.forma_operacao.nome,
        status_acesso_nome=deps.status_acessos.nome,
    )
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model, deps


async def delete_rpa(session: AsyncSession, nome: str) -> None:
    result = await session.execute(select(RPAModel).where(RPAModel.nome == nome))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()
