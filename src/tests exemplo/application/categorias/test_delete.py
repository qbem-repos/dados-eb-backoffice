import pytest
from fastapi import HTTPException

from src.application.contas.categorias import Categorias
from tests._tests_config import build_superadmin_scope, create_categoria, delete_categoria, validate_output


@pytest.mark.asyncio
async def test_delete_categoria_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_categoria(db_session)
    result = await Categorias.Delete.run(uuid=model.uuid, user_scope=scope, local_session=db_session)
    validate_output(Categorias.Delete.Output, result)


@pytest.mark.asyncio
async def test_delete_categoria_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Categorias.Delete.run(uuid="nao_existe", user_scope=scope, local_session=db_session)
