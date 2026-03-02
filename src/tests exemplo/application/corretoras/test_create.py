import pytest
from fastapi import HTTPException

from src.application.contas.corretoras import Corretoras
from tests._tests_config import build_superadmin_scope, create_corretora, delete_corretora, validate_output


@pytest.mark.asyncio
async def test_create_corretora_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Corretoras.Create.Input(uuid="corretora_test_1", estipulantes=["A"], id_corretora_eb=123)
    model = await Corretoras.Create.run(data=data, user_scope=scope, local_session=db_session)
    try:
        validate_output(Corretoras.Create.Output, model)
        assert model.uuid == data.uuid
    finally:
        await delete_corretora(db_session, model.uuid)


@pytest.mark.asyncio
async def test_create_corretora_duplicate(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    existing = await create_corretora(db_session, uuid="corretora_test_dup")
    try:
        data = Corretoras.Create.Input(uuid=existing.uuid)
        with pytest.raises(HTTPException):
            await Corretoras.Create.run(data=data, user_scope=scope, local_session=db_session)
    finally:
        await delete_corretora(db_session, existing.uuid)
