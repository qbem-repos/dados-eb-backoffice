import pytest
from fastapi import HTTPException

from src.application.contas.modulos import Modulos
from tests._tests_config import build_superadmin_scope, create_modulo, delete_modulo, validate_output


@pytest.mark.asyncio
async def test_create_modulo_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Modulos.Create.Input(uuid="modulo_test_1")
    model = await Modulos.Create.run(data=data, user_scope=scope, local_session=db_session)
    try:
        validate_output(Modulos.Create.Output, model)
        assert model.uuid == data.uuid
    finally:
        await delete_modulo(db_session, model.uuid)


@pytest.mark.asyncio
async def test_create_modulo_duplicate(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    existing = await create_modulo(db_session, uuid="modulo_test_dup")
    try:
        data = Modulos.Create.Input(uuid=existing.uuid)
        with pytest.raises(HTTPException):
            await Modulos.Create.run(data=data, user_scope=scope, local_session=db_session)
    finally:
        await delete_modulo(db_session, existing.uuid)
