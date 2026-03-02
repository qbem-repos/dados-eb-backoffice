import pytest
from fastapi import HTTPException
from sqlalchemy import select

from src.application.rpas.processo import ProcessoService
from src.data.db_backoffice_eb.models.rpas import ProcessoModel
from tests._tests_config import (
    validate_output,
    make_nome,
    create_processo,
    delete_processo,
)


@pytest.mark.asyncio
async def test_create_processo_success(db_session, user_scope):
    data = ProcessoService.Create.Input(nome=make_nome("processo"))
    model = await ProcessoService.Create.create_processo(
        data=data,
        user_scope=user_scope,
        session=db_session,
        user_id=user_scope.user_id,
    )
    try:
        validate_output(ProcessoService.Create.Output, model)
        assert model.nome == data.nome
    finally:
        await delete_processo(db_session, model.nome)


@pytest.mark.asyncio
async def test_create_processo_duplicate(db_session, user_scope):
    existing = await create_processo(db_session, nome=make_nome("processo_dup"))
    existing_nome = existing.nome
    db_session.expunge(existing)
    try:
        data = ProcessoService.Create.Input(nome=existing_nome)
        with pytest.raises(HTTPException) as exc:
            await ProcessoService.Create.create_processo(
                data=data,
                user_scope=user_scope,
                session=db_session,
                user_id=user_scope.user_id,
            )
        assert exc.value.status_code == 409
    finally:
        await delete_processo(db_session, existing_nome)


@pytest.mark.asyncio
async def test_get_processo_success(db_session, user_scope):
    existing = await create_processo(db_session, nome=make_nome("processo_get"))
    try:
        data = ProcessoService.Read.Input(nome=existing.nome)
        model = await ProcessoService.Read.get_processo(data, user_scope, db_session)
        assert model.nome == existing.nome
    finally:
        await delete_processo(db_session, existing.nome)


@pytest.mark.asyncio
async def test_list_processos_success(db_session, user_scope):
    prefix = make_nome("processo_list")
    first = await create_processo(db_session, nome=f"{prefix}_1")
    second = await create_processo(db_session, nome=f"{prefix}_2")
    try:
        data = ProcessoService.List.Input(nome=prefix)
        items = await ProcessoService.List.list_processos(data, user_scope, db_session)
        nomes = {item.nome for item in items}
        assert first.nome in nomes
        assert second.nome in nomes
    finally:
        await delete_processo(db_session, first.nome)
        await delete_processo(db_session, second.nome)


@pytest.mark.asyncio
async def test_update_processo_success(db_session, user_scope):
    existing = await create_processo(db_session, nome=make_nome("processo_upd"))
    novo_nome = make_nome("processo_novo")
    try:
        data = ProcessoService.Update.Input(nome_atual=existing.nome, novo_nome=novo_nome)
        model = await ProcessoService.Update.update_processo(
            data,
            user_scope,
            db_session,
            user_id=user_scope.user_id,
        )
        assert model.nome == novo_nome
    finally:
        await delete_processo(db_session, novo_nome)


@pytest.mark.asyncio
async def test_delete_processo_success(db_session, user_scope):
    existing = await create_processo(db_session, nome=make_nome("processo_del"))
    data = ProcessoService.Delete.Input(nome=existing.nome)
    await ProcessoService.Delete.delete_processo(data, user_scope, db_session)
    result = await db_session.execute(select(ProcessoModel).where(ProcessoModel.nome == existing.nome))
    assert result.scalars().one_or_none() is None
