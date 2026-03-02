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
async def test_create_user_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Usuarios.Create.Input(
        name="Usuario Criado",
        email=f"novo_user_{uuid4().hex}@test.local",
        password="Senha@12345",
        corretora_uuid=base_data.corretora_uuid,
        estipulante_uuid=None,
        perfil_uuid=base_data.perfil_uuid,
        usuario_categoria_uuid=base_data.categoria_uuid,
        active=True,
        super_admin=False,
    )

    user = await Usuarios.Create.run(data=data, user_scope=scope, local_session=db_session)
    try:
        payload = build_usuario_output_payload(user)
        validate_output(Usuarios.Create.Output, payload)
        assert user.email == data.email
    finally:
        await delete_user(db_session, user.id)


@pytest.mark.asyncio
async def test_create_user_duplicate_email(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    email = f"duplicado_{uuid4().hex}@test.local"
    existing = await create_user(
        db_session,
        email=email,
        corretora_uuid=base_data.corretora_uuid,
        perfil_uuid=base_data.perfil_uuid,
        categoria_uuid=base_data.categoria_uuid,
    )
    try:
        data = Usuarios.Create.Input(
            name="Usuario Duplicado",
            email=existing.email,
            password="Senha@12345",
        )
        with pytest.raises(HTTPException):
            await Usuarios.Create.run(data=data, user_scope=scope, local_session=db_session)
    finally:
        await delete_user(db_session, existing.id)
