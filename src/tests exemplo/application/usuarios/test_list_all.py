import pytest

from src.application.contas.usuarios import Usuarios
from tests._tests_config import (
    build_superadmin_scope,
    build_usuario_output_payload,
    create_user,
    delete_user,
    validate_output,
)


@pytest.mark.asyncio
async def test_list_all_users(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    user = await create_user(
        db_session,
        corretora_uuid=base_data.corretora_uuid,
        perfil_uuid=base_data.perfil_uuid,
        categoria_uuid=base_data.categoria_uuid,
    )
    try:
        result = await Usuarios.ListAll.run(user_scope=scope, local_session=db_session)
        assert any(item.id == user.id for item in result)
        for item in result:
            payload = build_usuario_output_payload(item)
            validate_output(Usuarios.ListAll.Output, payload)
    finally:
        await delete_user(db_session, user.id)
