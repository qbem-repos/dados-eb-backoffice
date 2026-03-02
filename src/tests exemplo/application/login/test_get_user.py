import pytest
from fastapi import HTTPException

from src.application.contas.login import LoginServices


@pytest.mark.asyncio
async def test_get_user_success(db_session, base_data):
    user = await LoginServices.GetUser.run(
        email=base_data.admin_email,
        password=base_data.admin_password,
        local_session=db_session,
    )
    assert user.email == base_data.admin_email


@pytest.mark.asyncio
async def test_get_user_invalid_password(db_session, base_data):
    with pytest.raises(HTTPException):
        await LoginServices.GetUser.run(
            email=base_data.admin_email,
            password="senha_errada",
            local_session=db_session,
        )


@pytest.mark.asyncio
async def test_get_user_not_found(db_session, base_data):
    with pytest.raises(HTTPException):
        await LoginServices.GetUser.run(
            email="nao_existe@test.local",
            password=base_data.admin_password,
            local_session=db_session,
        )
