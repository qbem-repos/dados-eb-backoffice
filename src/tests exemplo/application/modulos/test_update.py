import pytest
from fastapi import HTTPException

from src.application.contas.modulos import Modulos
from tests._tests_config import build_superadmin_scope, create_modulo, delete_modulo, validate_output


@pytest.mark.asyncio
async def test_update_modulo_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_modulo(db_session)
    try:
        data = Modulos.Update.Input(uuid=model.uuid, new_uuid="modulo_test_new")
        result = await Modulos.Update.run(data=data, user_scope=scope, local_session=db_session)
        validate_output(Modulos.Update.Output, result)
        assert result.uuid == data.new_uuid
    finally:
        await delete_modulo(db_session, data.new_uuid)


@pytest.mark.asyncio
async def test_update_modulo_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Modulos.Update.Input(uuid="nao_existe", new_uuid="modulo_novo")
    with pytest.raises(HTTPException):
        await Modulos.Update.run(data=data, user_scope=scope, local_session=db_session)
