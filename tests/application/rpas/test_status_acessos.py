import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.status_acessos import StatusAcessosService
from src.data.db_backoffice_eb.models.rpas import StatusAcessosModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_status_acessos,
    delete_status_acessos,
)


@pytest.mark.asyncio
async def test_create_status_acessos_success(db_session, user_scope):
    data = StatusAcessosService.Create.Input(nome=make_nome("status_acessos"))
    model = await StatusAcessosService.Create.create_status_acessos(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(StatusAcessosService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_status_acessos(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_status_acessos_duplicate(db_session, user_scope):
    existing = await create_status_acessos(db_session, nome=make_nome("status_acessos_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = StatusAcessosService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await StatusAcessosService.Create.create_status_acessos(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_status_acessos(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_status_acessos_success(db_session, user_scope):
    existing = await create_status_acessos(db_session, nome=make_nome("status_acessos_get"))
    try:
        data = StatusAcessosService.Read.Input(nome=existing.nome)
        model = await StatusAcessosService.Read.get_status_acessos(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_status_acessos(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_status_acessos_success(db_session, user_scope):
    prefix = make_nome("status_acessos_list")
    first = await create_status_acessos(db_session, nome=f"{prefix}_1")
    second = await create_status_acessos(db_session, nome=f"{prefix}_2")
    try:
        data = StatusAcessosService.List.Input(nome=prefix)
        items = await StatusAcessosService.List.list_status_acessos(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_status_acessos(db_session, first.nome)
        await delete_status_acessos(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_status_acessos_success(db_session, user_scope):
    existing = await create_status_acessos(db_session, nome=make_nome("status_acessos_upd"))
    novo_nome = make_nome("status_acessos_novo")
    try:
        data = StatusAcessosService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await StatusAcessosService.Update.update_status_acessos(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_status_acessos(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_status_acessos_success(db_session, user_scope):
    existing = await create_status_acessos(db_session, nome=make_nome("status_acessos_del"))
    data = StatusAcessosService.Delete.Input(nome=existing.nome)
    await StatusAcessosService.Delete.delete_status_acessos(data, user_scope, db_session)
    result = await db_session.execute(select(StatusAcessosModel).where(StatusAcessosModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
