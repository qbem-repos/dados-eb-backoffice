import pytest
from fastapi import HTTPException

from src.application.contas.perfis import Perfis
from tests._tests_config import (
    build_perfil_output_payload,
    build_superadmin_scope,
    create_perfil,
    delete_perfil,
    validate_output,
)


@pytest.mark.asyncio
async def test_get_perfil_by_id_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    perfil = await create_perfil(db_session)
    try:
        result = await Perfis.GetById.run(uuid=perfil.uuid, user_scope=scope, local_session=db_session)
        payload = build_perfil_output_payload(result)
        validate_output(Perfis.GetById.Output, payload)
        assert result.uuid == perfil.uuid
    finally:
        await delete_perfil(db_session, perfil.uuid)


@pytest.mark.asyncio
async def test_get_perfil_by_id_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Perfis.GetById.run(uuid="nao_existe", user_scope=scope, local_session=db_session)
