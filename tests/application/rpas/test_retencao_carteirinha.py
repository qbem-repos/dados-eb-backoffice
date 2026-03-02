import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.retencao_carteirinha import RetencaoCarteirinhaService
from src.data.db_backoffice_eb.models.rpas import RetencaoCarteirinhaModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_retencao_carteirinha,
    delete_retencao_carteirinha,
)


@pytest.mark.asyncio
async def test_create_retencao_carteirinha_success(db_session, user_scope):
    data = RetencaoCarteirinhaService.Create.Input(nome=make_nome("retencao"))
    model = await RetencaoCarteirinhaService.Create.create_retencao_carteirinha(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(RetencaoCarteirinhaService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_retencao_carteirinha(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_retencao_carteirinha_duplicate(db_session, user_scope):
    existing = await create_retencao_carteirinha(db_session, nome=make_nome("retencao_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = RetencaoCarteirinhaService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await RetencaoCarteirinhaService.Create.create_retencao_carteirinha(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_retencao_carteirinha(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_retencao_carteirinha_success(db_session, user_scope):
    existing = await create_retencao_carteirinha(db_session, nome=make_nome("retencao_get"))
    try:
        data = RetencaoCarteirinhaService.Read.Input(nome=existing.nome)
        model = await RetencaoCarteirinhaService.Read.get_retencao_carteirinha(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_retencao_carteirinha(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_retencoes_carteirinha_success(db_session, user_scope):
    prefix = make_nome("retencao_list")
    first = await create_retencao_carteirinha(db_session, nome=f"{prefix}_1")
    second = await create_retencao_carteirinha(db_session, nome=f"{prefix}_2")
    try:
        data = RetencaoCarteirinhaService.List.Input(nome=prefix)
        items = await RetencaoCarteirinhaService.List.list_retencoes_carteirinha(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_retencao_carteirinha(db_session, first.nome)
        await delete_retencao_carteirinha(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_retencao_carteirinha_success(db_session, user_scope):
    existing = await create_retencao_carteirinha(db_session, nome=make_nome("retencao_upd"))
    novo_nome = make_nome("retencao_novo")
    try:
        data = RetencaoCarteirinhaService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await RetencaoCarteirinhaService.Update.update_retencao_carteirinha(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_retencao_carteirinha(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_retencao_carteirinha_success(db_session, user_scope):
    existing = await create_retencao_carteirinha(db_session, nome=make_nome("retencao_del"))
    data = RetencaoCarteirinhaService.Delete.Input(nome=existing.nome)
    await RetencaoCarteirinhaService.Delete.delete_retencao_carteirinha(data, user_scope, db_session)
    result = await db_session.execute(
        select(RetencaoCarteirinhaModel).where(RetencaoCarteirinhaModel.nome == existing.nome)
    )
    assert result.scalars().one_or_none() is None
