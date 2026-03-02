import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.operadora import OperadoraService
from src.data.db_backoffice_eb.models.rpas import OperadoraModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_operadora,
    delete_operadora,
)


@pytest.mark.asyncio
async def test_create_operadora_success(db_session, user_scope):
    data = OperadoraService.Create.Input(nome=make_nome("operadora"))
    model = await OperadoraService.Create.create_operadora(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(OperadoraService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_operadora(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_operadora_duplicate(db_session, user_scope):
    existing = await create_operadora(db_session, nome=make_nome("operadora_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = OperadoraService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await OperadoraService.Create.create_operadora(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_operadora(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_operadora_success(db_session, user_scope):
    existing = await create_operadora(db_session, nome=make_nome("operadora_get"))
    try:
        data = OperadoraService.Read.Input(nome=existing.nome)
        model = await OperadoraService.Read.get_operadora(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_operadora(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_operadoras_success(db_session, user_scope):
    prefix = make_nome("operadora_list")
    first = await create_operadora(db_session, nome=f"{prefix}_1")
    second = await create_operadora(db_session, nome=f"{prefix}_2")
    try:
        data = OperadoraService.List.Input(nome=prefix)
        items = await OperadoraService.List.list_operadoras(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_operadora(db_session, first.nome)
        await delete_operadora(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_operadora_success(db_session, user_scope):
    existing = await create_operadora(db_session, nome=make_nome("operadora_upd"))
    novo_nome = make_nome("operadora_novo")
    try:
        data = OperadoraService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await OperadoraService.Update.update_operadora(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_operadora(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_operadora_success(db_session, user_scope):
    existing = await create_operadora(db_session, nome=make_nome("operadora_del"))
    data = OperadoraService.Delete.Input(nome=existing.nome)
    await OperadoraService.Delete.delete_operadora(data, user_scope, db_session)
    result = await db_session.execute(select(OperadoraModel).where(OperadoraModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
