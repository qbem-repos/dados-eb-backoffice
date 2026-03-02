import pytest
from fastapi import HTTPException

from src.application.contas.usuarios import Usuarios
from tests._tests_config import (
    build_superadmin_scope,
    build_usuario_output_payload,
    create_user,
    delete_user,
    validate_output,
)


@pytest.mark.asyncio
async def test_get_user_by_id_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    user = await create_user(
        db_session,
        corretora_uuid=base_data.corretora_uuid,
        perfil_uuid=base_data.perfil_uuid,
        categoria_uuid=base_data.categoria_uuid,
    )
    try:
        result = await Usuarios.GetById.run(user_id=user.id, user_scope=scope, local_session=db_session)
        payload = build_usuario_output_payload(result)
        validate_output(Usuarios.GetById.Output, payload)
        assert result.id == user.id
    finally:
        await delete_user(db_session, user.id)


@pytest.mark.asyncio
async def test_get_user_by_id_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Usuarios.GetById.run(user_id=-1, user_scope=scope, local_session=db_session)
