import pytest
from fastapi import HTTPException

from src.application.contas.perfis import Perfis
from tests._tests_config import build_superadmin_scope, create_perfil, delete_perfil, validate_output


@pytest.mark.asyncio
async def test_delete_perfil_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    perfil = await create_perfil(db_session)
    result = await Perfis.Delete.run(uuid=perfil.uuid, user_scope=scope, local_session=db_session)
    validate_output(Perfis.Delete.Output, result)


@pytest.mark.asyncio
async def test_delete_perfil_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Perfis.Delete.run(uuid="nao_existe", user_scope=scope, local_session=db_session)
