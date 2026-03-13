import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.app_security.user_scope import UserScope
from src.api_rest.auth import get_current_user
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.rpa import RPAService
from src.data.db_backoffice_eb.models.rpas import RPAModel


router = APIRouter(tags=["RPAs"], prefix="/rpas")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=RPAService.Create.Output)
async def create_rpa(
    data: RPAService.Create.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await RPAService.Create.create_rpa(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, RPAService.Create.Output)


@router.get("/bi", response_model=dict)
async def get_rpa_bi(
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    table_items = await RPAService.BI.list_full_table(
        user_scope,
        db_session,
    )
    output_model = RPAModel.to_pydantic_schema()
    table = [output_model.model_validate(item, from_attributes=True) for item in table_items]

    total = await RPAService.BI.total_rpas(user_scope, db_session)
    total_por_status = await RPAService.BI.total_por_status(user_scope, db_session)
    total_por_status_acesso = await RPAService.BI.total_por_status_acesso(user_scope, db_session)
    total_por_produto = await RPAService.BI.total_por_produto(user_scope, db_session)
    total_por_processo = await RPAService.BI.total_por_processo(user_scope, db_session)

    return {
        "tabela_rpas": table,
        "total_rpas": total,
        "total_por_status": total_por_status,
        "total_por_status_acesso": total_por_status_acesso,
        "total_por_produto": total_por_produto,
        "total_por_processo": total_por_processo,
    }


@router.get("/{rpa_id}", response_model=RPAService.Read.Output)
async def get_rpa(
    rpa_id: int,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = RPAService.Read.Input(id=rpa_id)
    model = await RPAService.Read.get_rpa(payload, user_scope, db_session)
    return _to_output(model, RPAService.Read.Output)


@router.get("", response_model=List[RPAService.List.Output])
async def list_rpas(
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    return await RPAService.List.list_rpas(user_scope, db_session)


@router.put("/{rpa_id}", response_model=RPAService.Update.Output)
async def update_rpa(
    rpa_id: int,
    data: RPAService.Update.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = RPAService.Update.Input(
        id=rpa_id,
        **data.model_dump(exclude_unset=True, exclude={"id"}),
    )
    model = await RPAService.Update.update_rpa(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, RPAService.Update.Output)


@router.delete("/{rpa_id}", response_model=dict)
async def delete_rpa(
    rpa_id: int,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = RPAService.Delete.Input(id=rpa_id)
    await RPAService.Delete.delete_rpa(payload, user_scope, db_session)
    return {"deleted": True}
