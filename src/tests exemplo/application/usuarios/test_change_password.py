import pytest
from fastapi import HTTPException

from src.application.contas.usuarios import Usuarios
from shareds.services.app_security.user_scope import UserScope
from tests._tests_config import build_superadmin_scope, create_user, delete_user, validate_output


@pytest.mark.asyncio
async def test_change_password_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    user = await create_user(db_session)
    try:
        data = Usuarios.ChangePassword.Input(user_id=user.id, new_password="NovaSenha@123")
        result = await Usuarios.ChangePassword.run(data=data, user_scope=scope, local_session=db_session)
        validate_output(Usuarios.ChangePassword.Output, result)
        assert result["updated"] is True
    finally:
        await delete_user(db_session, user.id)


@pytest.mark.asyncio
async def test_change_password_unauthorized(db_session, base_data):
    user = await create_user(db_session)
    try:
        scope = UserScope(
            user_id=base_data.admin_user_id,
            nome="Usuario",
            email=base_data.admin_email,
            corretora=base_data.corretora_uuid,
            estipulante=None,
            ativo=True,
            superadmin=False,
            perfil=base_data.perfil_uuid,
            modulos=[base_data.modulo_uuid],
            categoria=base_data.categoria_uuid,
        )
        data = Usuarios.ChangePassword.Input(user_id=user.id, new_password="OutraSenha@123")
        with pytest.raises(HTTPException):
            await Usuarios.ChangePassword.run(data=data, user_scope=scope, local_session=db_session)
    finally:
        await delete_user(db_session, user.id)
