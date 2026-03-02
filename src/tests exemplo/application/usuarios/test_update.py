import pytest
from fastapi import HTTPException
from uuid import uuid4

from src.application.contas.usuarios import Usuarios
from tests._tests_config import (
    build_superadmin_scope,
    build_usuario_output_payload,
    create_user,
    delete_user,
    validate_output,
)


@pytest.mark.asyncio
async def test_update_user_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    user = await create_user(
        db_session,
        email=f"update_user_{uuid4().hex}@test.local",
        corretora_uuid=base_data.corretora_uuid,
        perfil_uuid=base_data.perfil_uuid,
        categoria_uuid=base_data.categoria_uuid,
    )
    try:
        data = Usuarios.Update.Input(
            id=user.id,
            name="Usuario Atualizado",
            email=f"update_user_new_{uuid4().hex}@test.local",
            active=False,
        )
        result = await Usuarios.Update.run(data=data, user_scope=scope, local_session=db_session)
        payload = build_usuario_output_payload(result)
        validate_output(Usuarios.Update.Output, payload)
        assert result.email == data.email
    finally:
        await delete_user(db_session, user.id)


@pytest.mark.asyncio
async def test_update_user_email_in_use(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    first = await create_user(db_session, email=f"first_{uuid4().hex}@test.local")
    second = await create_user(db_session, email=f"second_{uuid4().hex}@test.local")
    try:
        data = Usuarios.Update.Input(id=second.id, email=first.email)
        with pytest.raises(HTTPException):
            await Usuarios.Update.run(data=data, user_scope=scope, local_session=db_session)
    finally:
        await delete_user(db_session, first.id)
        await delete_user(db_session, second.id)


@pytest.mark.asyncio
async def test_update_user_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Usuarios.Update.Input(id=-1, name="Nao Existe")
    with pytest.raises(HTTPException):
        await Usuarios.Update.run(data=data, user_scope=scope, local_session=db_session)
