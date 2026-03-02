import pytest

from src.application.contas.categorias import Categorias
from tests._tests_config import build_superadmin_scope, create_categoria, delete_categoria, validate_output


@pytest.mark.asyncio
async def test_list_all_categorias(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_categoria(db_session)
    try:
        result = await Categorias.ListAll.run(user_scope=scope, local_session=db_session)
        assert any(item.uuid == model.uuid for item in result)
        for item in result:
            validate_output(Categorias.ListAll.Output, item)
    finally:
        await delete_categoria(db_session, model.uuid)
