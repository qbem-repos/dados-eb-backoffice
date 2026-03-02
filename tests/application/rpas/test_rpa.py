import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.rpa import RPAService
from src.data.db_backoffice_eb.models.rpas import RPAModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_rpa,
    delete_rpa,
    create_rpa_dependencies,
    cleanup_rpa_dependencies,
    snapshot_rpa_dependency_names,
    cleanup_rpa_dependencies_by_names,
)


@pytest.mark.asyncio
async def test_create_rpa_success(db_session, user_scope):
    deps = await create_rpa_dependencies(db_session)
    data = RPAService.Create.Input(
        nome=make_nome("rpa"),
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
        status_detalhe=None,
        status_last_update=None,
        status_acesso_detalhe=None,
        status_acesso_last_update=None,
    )
    model = await RPAService.Create.create_rpa(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(RPAService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_rpa(db_session, model.nome)
        await cleanup_rpa_dependencies(db_session, deps)


@pytest.mark.asyncio
async def test_create_rpa_duplicate(db_session, user_scope):
    model, deps = await create_rpa(db_session)
    model_nome = model.nome
    deps_names = snapshot_rpa_dependency_names(deps)
    try:
        data = RPAService.Create.Input(
            nome=model_nome,
            operadora_nome=deps_names.operadora_nome,
            produto_nome=deps_names.produto_nome,
            tipo_contrato_nome=deps_names.tipo_contrato_nome,
            processo_nome=deps_names.processo_nome,
            tipo_rpa_nome=deps_names.tipo_rpa_nome,
            status_nome=deps_names.status_nome,
            retencao_carteirinha_nome=deps_names.retencao_nome,
            doc_baixa=None,
            forma_operacao_nome=deps_names.forma_operacao_nome,
            status_acesso_nome=deps_names.status_acessos_nome,
            status_detalhe=None,
            status_last_update=None,
            status_acesso_detalhe=None,
            status_acesso_last_update=None,
        )
        with pytest.raises(HTTPException) as exc:
            await RPAService.Create.create_rpa(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_rpa(db_session, model_nome)
        await cleanup_rpa_dependencies_by_names(db_session, deps_names)


@pytest.mark.asyncio
async def test_get_rpa_success(db_session, user_scope):
    model, deps = await create_rpa(db_session)
    try:
        data = RPAService.Read.Input(id=model.id)
        result = await RPAService.Read.get_rpa(data, user_scope, db_session)
        assert result.nome == model.nome
    finally:
        await delete_rpa(db_session, model.nome)
        await cleanup_rpa_dependencies(db_session, deps)


@pytest.mark.asyncio
async def test_list_rpas_success(db_session, user_scope):
    model, deps = await create_rpa(db_session, nome=make_nome("rpa_list"))
    try:
        items = await RPAService.List.list_rpas(user_scope, db_session)
        ids = {item.id for item in items}
        assert model.id in ids
    finally:
        await delete_rpa(db_session, model.nome)
        await cleanup_rpa_dependencies(db_session, deps)


@pytest.mark.asyncio
async def test_update_rpa_success(db_session, user_scope):
    model, deps = await create_rpa(db_session, nome=make_nome("rpa_upd"))
    novo_nome = make_nome("rpa_novo")
    try:
        data = RPAService.Update.Input(id=model.id, novo_nome=novo_nome)
        updated = await RPAService.Update.update_rpa(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert updated.nome == novo_nome
    finally:
        await delete_rpa(db_session, novo_nome)
        await cleanup_rpa_dependencies(db_session, deps)


@pytest.mark.asyncio
async def test_delete_rpa_success(db_session, user_scope):
    model, deps = await create_rpa(db_session)
    data = RPAService.Delete.Input(id=model.id)
    await RPAService.Delete.delete_rpa(data, user_scope, db_session)
    result = await db_session.execute(select(RPAModel).where(RPAModel.nome == model.nome))
    assert result.scalars().one_or_none() is None
    await cleanup_rpa_dependencies(db_session, deps)
