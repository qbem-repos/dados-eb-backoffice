import pytest
from fastapi import HTTPException

from src.application.contas.perfis import Perfis
from tests._tests_config import (
    build_perfil_output_payload,
    build_superadmin_scope,
    create_modulo,
    create_perfil,
    delete_modulo,
    delete_perfil,
    validate_output,
)


@pytest.mark.asyncio
async def test_update_perfil_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    perfil = await create_perfil(db_session, uuid="perfil_update")
    modulo = await create_modulo(db_session, uuid="perfil_modulo_update")
    try:
        data = Perfis.Update.Input(uuid=perfil.uuid, new_uuid="perfil_update_new", modulo_uuids=[modulo.uuid])
        result = await Perfis.Update.run(data=data, user_scope=scope, local_session=db_session)
        payload = build_perfil_output_payload(result)
        validate_output(Perfis.Update.Output, payload)
        assert result.uuid == data.new_uuid
    finally:
        await delete_perfil(db_session, "perfil_update_new")
        await delete_modulo(db_session, modulo.uuid)


@pytest.mark.asyncio
async def test_update_perfil_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Perfis.Update.Input(uuid="nao_existe", new_uuid="perfil_novo")
    with pytest.raises(HTTPException):
        await Perfis.Update.run(data=data, user_scope=scope, local_session=db_session)
