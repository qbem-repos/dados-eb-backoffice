import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.forma_operacao import FormaOperacaoService
from src.data.db_backoffice_eb.models.rpas import FormaOperacaoModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_forma_operacao,
    delete_forma_operacao,
)


@pytest.mark.asyncio
async def test_create_forma_operacao_success(db_session, user_scope):
    data = FormaOperacaoService.Create.Input(nome=make_nome("forma_operacao"))
    model = await FormaOperacaoService.Create.create_forma_operacao(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(FormaOperacaoService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_forma_operacao(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_forma_operacao_duplicate(db_session, user_scope):
    existing = await create_forma_operacao(db_session, nome=make_nome("forma_operacao_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = FormaOperacaoService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await FormaOperacaoService.Create.create_forma_operacao(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_forma_operacao(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_forma_operacao_success(db_session, user_scope):
    existing = await create_forma_operacao(db_session, nome=make_nome("forma_operacao_get"))
    try:
        data = FormaOperacaoService.Read.Input(nome=existing.nome)
        model = await FormaOperacaoService.Read.get_forma_operacao(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_forma_operacao(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_formas_operacao_success(db_session, user_scope):
    prefix = make_nome("forma_operacao_list")
    first = await create_forma_operacao(db_session, nome=f"{prefix}_1")
    second = await create_forma_operacao(db_session, nome=f"{prefix}_2")
    try:
        data = FormaOperacaoService.List.Input(nome=prefix)
        items = await FormaOperacaoService.List.list_formas_operacao(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_forma_operacao(db_session, first.nome)
        await delete_forma_operacao(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_forma_operacao_success(db_session, user_scope):
    existing = await create_forma_operacao(db_session, nome=make_nome("forma_operacao_upd"))
    novo_nome = make_nome("forma_operacao_novo")
    try:
        data = FormaOperacaoService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await FormaOperacaoService.Update.update_forma_operacao(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_forma_operacao(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_forma_operacao_success(db_session, user_scope):
    existing = await create_forma_operacao(db_session, nome=make_nome("forma_operacao_del"))
    data = FormaOperacaoService.Delete.Input(nome=existing.nome)
    await FormaOperacaoService.Delete.delete_forma_operacao(data, user_scope, db_session)
    result = await db_session.execute(select(FormaOperacaoModel).where(FormaOperacaoModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
