import pytest
from fastapi import HTTPException

from src.application.contas.corretoras import Corretoras
from tests._tests_config import build_superadmin_scope, create_corretora, delete_corretora, validate_output


@pytest.mark.asyncio
async def test_update_corretora_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_corretora(db_session)
    try:
        data = Corretoras.Update.Input(uuid=model.uuid, estipulantes=["B"], id_corretora_eb=999)
        result = await Corretoras.Update.run(data=data, user_scope=scope, local_session=db_session)
        validate_output(Corretoras.Update.Output, result)
        assert result.id_corretora_eb == 999
    finally:
        await delete_corretora(db_session, model.uuid)


@pytest.mark.asyncio
async def test_update_corretora_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    data = Corretoras.Update.Input(uuid="nao_existe", estipulantes=["X"])
    with pytest.raises(HTTPException):
        await Corretoras.Update.run(data=data, user_scope=scope, local_session=db_session)
