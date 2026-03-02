import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.tipo_contrato import TipoContratoService
from src.data.db_backoffice_eb.models.rpas import TipoContratoModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_tipo_contrato,
    delete_tipo_contrato,
)


@pytest.mark.asyncio
async def test_create_tipo_contrato_success(db_session, user_scope):
    data = TipoContratoService.Create.Input(nome=make_nome("tipo_contrato"))
    model = await TipoContratoService.Create.create_tipo_contrato(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(TipoContratoService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_tipo_contrato(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_tipo_contrato_duplicate(db_session, user_scope):
    existing = await create_tipo_contrato(db_session, nome=make_nome("tipo_contrato_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = TipoContratoService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await TipoContratoService.Create.create_tipo_contrato(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_tipo_contrato(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_tipo_contrato_success(db_session, user_scope):
    existing = await create_tipo_contrato(db_session, nome=make_nome("tipo_contrato_get"))
    try:
        data = TipoContratoService.Read.Input(nome=existing.nome)
        model = await TipoContratoService.Read.get_tipo_contrato(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_tipo_contrato(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_tipos_contrato_success(db_session, user_scope):
    prefix = make_nome("tipo_contrato_list")
    first = await create_tipo_contrato(db_session, nome=f"{prefix}_1")
    second = await create_tipo_contrato(db_session, nome=f"{prefix}_2")
    try:
        data = TipoContratoService.List.Input(nome=prefix)
        items = await TipoContratoService.List.list_tipos_contrato(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_tipo_contrato(db_session, first.nome)
        await delete_tipo_contrato(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_tipo_contrato_success(db_session, user_scope):
    existing = await create_tipo_contrato(db_session, nome=make_nome("tipo_contrato_upd"))
    novo_nome = make_nome("tipo_contrato_novo")
    try:
        data = TipoContratoService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await TipoContratoService.Update.update_tipo_contrato(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_tipo_contrato(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_tipo_contrato_success(db_session, user_scope):
    existing = await create_tipo_contrato(db_session, nome=make_nome("tipo_contrato_del"))
    data = TipoContratoService.Delete.Input(nome=existing.nome)
    await TipoContratoService.Delete.delete_tipo_contrato(data, user_scope, db_session)
    result = await db_session.execute(select(TipoContratoModel).where(TipoContratoModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
