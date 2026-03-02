import pytest

from src.application.contas.corretoras import Corretoras
from tests._tests_config import build_superadmin_scope, create_corretora, delete_corretora, validate_output


@pytest.mark.asyncio
async def test_list_all_corretoras(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_corretora(db_session)
    try:
        result = await Corretoras.ListAll.run(user_scope=scope, local_session=db_session)
        assert any(item.uuid == model.uuid for item in result)
        for item in result:
            validate_output(Corretoras.ListAll.Output, item)
    finally:
        await delete_corretora(db_session, model.uuid)
