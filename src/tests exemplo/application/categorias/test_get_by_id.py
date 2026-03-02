import pytest
from fastapi import HTTPException

from src.application.contas.categorias import Categorias
from tests._tests_config import build_superadmin_scope, create_categoria, delete_categoria, validate_output


@pytest.mark.asyncio
async def test_get_categoria_by_id_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_categoria(db_session)
    try:
        result = await Categorias.GetById.run(uuid=model.uuid, user_scope=scope, local_session=db_session)
        validate_output(Categorias.GetById.Output, result)
        assert result.uuid == model.uuid
    finally:
        await delete_categoria(db_session, model.uuid)


@pytest.mark.asyncio
async def test_get_categoria_by_id_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Categorias.GetById.run(uuid="nao_existe", user_scope=scope, local_session=db_session)
