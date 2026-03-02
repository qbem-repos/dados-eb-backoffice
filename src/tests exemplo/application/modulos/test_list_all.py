import pytest

from src.application.contas.modulos import Modulos
from tests._tests_config import build_superadmin_scope, create_modulo, delete_modulo, validate_output


@pytest.mark.asyncio
async def test_list_all_modulos(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_modulo(db_session)
    try:
        result = await Modulos.ListAll.run(user_scope=scope, local_session=db_session)
        assert any(item.uuid == model.uuid for item in result)
        for item in result:
            validate_output(Modulos.ListAll.Output, item)
    finally:
        await delete_modulo(db_session, model.uuid)
