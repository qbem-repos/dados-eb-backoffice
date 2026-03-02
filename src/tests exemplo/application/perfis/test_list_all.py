import pytest

from src.application.contas.perfis import Perfis
from tests._tests_config import (
    build_perfil_output_payload,
    build_superadmin_scope,
    create_perfil,
    delete_perfil,
    validate_output,
)


@pytest.mark.asyncio
async def test_list_all_perfis(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    perfil = await create_perfil(db_session)
    try:
        result = await Perfis.ListAll.run(user_scope=scope, local_session=db_session)
        assert any(item.uuid == perfil.uuid for item in result)
        for item in result:
            payload = build_perfil_output_payload(item)
            validate_output(Perfis.ListAll.Output, payload)
    finally:
        await delete_perfil(db_session, perfil.uuid)
