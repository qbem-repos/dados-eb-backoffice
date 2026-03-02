import pytest
from fastapi import HTTPException

from src.application.contas.usuarios import Usuarios
from tests._tests_config import build_superadmin_scope, create_user, delete_user, validate_output


@pytest.mark.asyncio
async def test_delete_user_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    user = await create_user(db_session)
    result = await Usuarios.Delete.run(user_id=user.id, user_scope=scope, local_session=db_session)
    validate_output(Usuarios.Delete.Output, result)


@pytest.mark.asyncio
async def test_delete_user_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Usuarios.Delete.run(user_id=-1, user_scope=scope, local_session=db_session)
