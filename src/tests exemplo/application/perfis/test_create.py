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
async def test_create_perfil_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    modulo = await create_modulo(db_session, uuid="perfil_modulo_1")
    try:
        data = Perfis.Create.Input(uuid="perfil_test_1", modulo_uuids=[modulo.uuid])
        perfil = await Perfis.Create.run(data=data, user_scope=scope, local_session=db_session)
        payload = build_perfil_output_payload(perfil)
        validate_output(Perfis.Create.Output, payload)
        assert perfil.uuid == data.uuid
    finally:
        await delete_perfil(db_session, "perfil_test_1")
        await delete_modulo(db_session, modulo.uuid)


@pytest.mark.asyncio
async def test_create_perfil_duplicate(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    perfil = await create_perfil(db_session, uuid="perfil_dup")
    try:
        data = Perfis.Create.Input(uuid=perfil.uuid)
        with pytest.raises(HTTPException):
            await Perfis.Create.run(data=data, user_scope=scope, local_session=db_session)
    finally:
        await delete_perfil(db_session, perfil.uuid)
