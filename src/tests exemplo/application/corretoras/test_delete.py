import pytest
from fastapi import HTTPException

from src.application.contas.corretoras import Corretoras
from tests._tests_config import build_superadmin_scope, create_corretora, delete_corretora, validate_output


@pytest.mark.asyncio
async def test_delete_corretora_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_corretora(db_session)
    result = await Corretoras.Delete.run(uuid=model.uuid, user_scope=scope, local_session=db_session)
    validate_output(Corretoras.Delete.Output, result)


@pytest.mark.asyncio
async def test_delete_corretora_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Corretoras.Delete.run(uuid="nao_existe", user_scope=scope, local_session=db_session)
