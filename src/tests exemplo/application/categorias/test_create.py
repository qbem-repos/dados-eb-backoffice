import pytest
from fastapi import HTTPException

from src.application.contas.categorias import Categorias
from tests._tests_config import build_superadmin_scope, create_categoria, delete_categoria, validate_output


@pytest.mark.asyncio
async def test_create_categoria_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Categorias.Create.Input(uuid="categoria_test_1")
    model = await Categorias.Create.run(data=data, user_scope=scope, local_session=db_session)
    try:
        validate_output(Categorias.Create.Output, model)
        assert model.uuid == data.uuid
    finally:
        await delete_categoria(db_session, model.uuid)


@pytest.mark.asyncio
async def test_create_categoria_duplicate(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    existing = await create_categoria(db_session, uuid="categoria_test_dup")
    try:
        data = Categorias.Create.Input(uuid=existing.uuid)
        with pytest.raises(HTTPException):
            await Categorias.Create.run(data=data, user_scope=scope, local_session=db_session)
    finally:
        await delete_categoria(db_session, existing.uuid)
