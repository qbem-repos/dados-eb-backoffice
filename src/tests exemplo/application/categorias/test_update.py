import pytest
from fastapi import HTTPException

from src.application.contas.categorias import Categorias
from tests._tests_config import build_superadmin_scope, create_categoria, delete_categoria, validate_output


@pytest.mark.asyncio
async def test_update_categoria_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_categoria(db_session)
    try:
        data = Categorias.Update.Input(uuid=model.uuid, new_uuid="categoria_test_new")
        result = await Categorias.Update.run(data=data, user_scope=scope, local_session=db_session)
        validate_output(Categorias.Update.Output, result)
        assert result.uuid == data.new_uuid
    finally:
        await delete_categoria(db_session, data.new_uuid)


@pytest.mark.asyncio
async def test_update_categoria_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Categorias.Update.Input(uuid="nao_existe", new_uuid="categoria_nova")
    with pytest.raises(HTTPException):
        await Categorias.Update.run(data=data, user_scope=scope, local_session=db_session)
