import pytest
from fastapi import HTTPException

from src.application.contas.login import LoginServices
from shareds.services.app_security.user_scope import UserScope
from tests._tests_config import build_superadmin_scope


@pytest.mark.asyncio
async def test_refresh_token_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    user = await LoginServices.RefreshToken.run(
        user_scope=scope,
        local_session=db_session,
    )
    assert user.id == base_data.admin_user_id


@pytest.mark.asyncio
async def test_refresh_token_not_found(db_session, base_data):
    scope = UserScope(
        user_id=-999,
        nome="Ghost",
        email="ghost@test.local",
        corretora=None,
        estipulante=None,
        ativo=True,
        superadmin=True,
        perfil=None,
        modulos=[],
        categoria=None,
    )
    with pytest.raises(HTTPException):
        await LoginServices.RefreshToken.run(
            user_scope=scope,
            local_session=db_session,
        )
