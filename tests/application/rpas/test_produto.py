import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.produto import ProdutoService
from src.data.db_backoffice_eb.models.rpas import ProdutoModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_produto,
    delete_produto,
)


@pytest.mark.asyncio
async def test_create_produto_success(db_session, user_scope):
    data = ProdutoService.Create.Input(nome=make_nome("produto"))
    model = await ProdutoService.Create.create_produto(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(ProdutoService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_produto(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_produto_duplicate(db_session, user_scope):
    existing = await create_produto(db_session, nome=make_nome("produto_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = ProdutoService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await ProdutoService.Create.create_produto(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_produto(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_produto_success(db_session, user_scope):
    existing = await create_produto(db_session, nome=make_nome("produto_get"))
    try:
        data = ProdutoService.Read.Input(nome=existing.nome)
        model = await ProdutoService.Read.get_produto(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_produto(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_produtos_success(db_session, user_scope):
    prefix = make_nome("produto_list")
    first = await create_produto(db_session, nome=f"{prefix}_1")
    second = await create_produto(db_session, nome=f"{prefix}_2")
    try:
        data = ProdutoService.List.Input(nome=prefix)
        items = await ProdutoService.List.list_produtos(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_produto(db_session, first.nome)
        await delete_produto(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_produto_success(db_session, user_scope):
    existing = await create_produto(db_session, nome=make_nome("produto_upd"))
    novo_nome = make_nome("produto_novo")
    try:
        data = ProdutoService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await ProdutoService.Update.update_produto(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_produto(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_produto_success(db_session, user_scope):
    existing = await create_produto(db_session, nome=make_nome("produto_del"))
    data = ProdutoService.Delete.Input(nome=existing.nome)
    await ProdutoService.Delete.delete_produto(data, user_scope, db_session)
    result = await db_session.execute(select(ProdutoModel).where(ProdutoModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
