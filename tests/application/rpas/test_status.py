import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.status import StatusService
from src.data.db_backoffice_eb.models.rpas import StatusModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_status,
    delete_status,
)


@pytest.mark.asyncio
async def test_create_status_success(db_session, user_scope):
    data = StatusService.Create.Input(nome=make_nome("status"))
    model = await StatusService.Create.create_status(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(StatusService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_status(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_status_duplicate(db_session, user_scope):
    existing = await create_status(db_session, nome=make_nome("status_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = StatusService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await StatusService.Create.create_status(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_status(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_status_success(db_session, user_scope):
    existing = await create_status(db_session, nome=make_nome("status_get"))
    try:
        data = StatusService.Read.Input(nome=existing.nome)
        model = await StatusService.Read.get_status(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_status(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_status_success(db_session, user_scope):
    prefix = make_nome("status_list")
    first = await create_status(db_session, nome=f"{prefix}_1")
    second = await create_status(db_session, nome=f"{prefix}_2")
    try:
        data = StatusService.List.Input(nome=prefix)
        items = await StatusService.List.list_status(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_status(db_session, first.nome)
        await delete_status(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_status_success(db_session, user_scope):
    existing = await create_status(db_session, nome=make_nome("status_upd"))
    novo_nome = make_nome("status_novo")
    try:
        data = StatusService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await StatusService.Update.update_status(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_status(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_status_success(db_session, user_scope):
    existing = await create_status(db_session, nome=make_nome("status_del"))
    data = StatusService.Delete.Input(nome=existing.nome)
    await StatusService.Delete.delete_status(data, user_scope, db_session)
    result = await db_session.execute(select(StatusModel).where(StatusModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
