import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.tipo_rpa import TipoRPAService
from src.data.db_backoffice_eb.models.rpas import TipoRPAModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_tipo_rpa,
    delete_tipo_rpa,
)


@pytest.mark.asyncio
async def test_create_tipo_rpa_success(db_session, user_scope):
    data = TipoRPAService.Create.Input(nome=make_nome("tipo_rpa"))
    model = await TipoRPAService.Create.create_tipo_rpa(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(TipoRPAService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_tipo_rpa(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_tipo_rpa_duplicate(db_session, user_scope):
    existing = await create_tipo_rpa(db_session, nome=make_nome("tipo_rpa_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = TipoRPAService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await TipoRPAService.Create.create_tipo_rpa(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_tipo_rpa(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_tipo_rpa_success(db_session, user_scope):
    existing = await create_tipo_rpa(db_session, nome=make_nome("tipo_rpa_get"))
    try:
        data = TipoRPAService.Read.Input(nome=existing.nome)
        model = await TipoRPAService.Read.get_tipo_rpa(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_tipo_rpa(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_tipos_rpa_success(db_session, user_scope):
    prefix = make_nome("tipo_rpa_list")
    first = await create_tipo_rpa(db_session, nome=f"{prefix}_1")
    second = await create_tipo_rpa(db_session, nome=f"{prefix}_2")
    try:
        data = TipoRPAService.List.Input(nome=prefix)
        items = await TipoRPAService.List.list_tipos_rpa(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_tipo_rpa(db_session, first.nome)
        await delete_tipo_rpa(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_tipo_rpa_success(db_session, user_scope):
    existing = await create_tipo_rpa(db_session, nome=make_nome("tipo_rpa_upd"))
    novo_nome = make_nome("tipo_rpa_novo")
    try:
        data = TipoRPAService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await TipoRPAService.Update.update_tipo_rpa(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_tipo_rpa(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_tipo_rpa_success(db_session, user_scope):
    existing = await create_tipo_rpa(db_session, nome=make_nome("tipo_rpa_del"))
    data = TipoRPAService.Delete.Input(nome=existing.nome)
    await TipoRPAService.Delete.delete_tipo_rpa(data, user_scope, db_session)
    result = await db_session.execute(select(TipoRPAModel).where(TipoRPAModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
