import pytest
from fastapi import HTTPException

from src.application.contas.modulos import Modulos
from tests._tests_config import build_superadmin_scope, create_modulo, delete_modulo, validate_output


@pytest.mark.asyncio
async def test_delete_modulo_success(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    model = await create_modulo(db_session)
    result = await Modulos.Delete.run(uuid=model.uuid, user_scope=scope, local_session=db_session)
    validate_output(Modulos.Delete.Output, result)


@pytest.mark.asyncio
async def test_delete_modulo_not_found(db_session, base_data):
    scope = build_superadmin_scope(base_data)
    with pytest.raises(HTTPException):
        await Modulos.Delete.run(uuid="nao_existe", user_scope=scope, local_session=db_session)
