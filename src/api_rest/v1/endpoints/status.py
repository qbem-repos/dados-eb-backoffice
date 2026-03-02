import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.api_utils.jwt_token import JWTToken
from shareds.services.app_security.user_scope import UserScope
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.status import StatusService


router = APIRouter(tags=["Status"], prefix="/status")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=StatusService.Create.Output)
async def create_status(
    data: StatusService.Create.Input,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await StatusService.Create.create_status(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, StatusService.Create.Output)


@router.get("/{nome}", response_model=StatusService.Read.Output)
async def get_status(
    nome: str,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusService.Read.Input(nome=nome)
    model = await StatusService.Read.get_status(payload, user_scope, db_session)
    return _to_output(model, StatusService.Read.Output)


@router.get("", response_model=List[StatusService.List.Input])
async def list_status(
    nome: str | None = None,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusService.List.Input(nome=nome)
    items = await StatusService.List.list_status(payload, user_scope, db_session)
    return [_to_output(item, StatusService.List.Input) for item in items]


@router.put("/{nome}", response_model=StatusService.Update.Output)
async def update_status(
    nome: str,
    data: StatusService.Update.Input,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await StatusService.Update.update_status(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, StatusService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_status(
    nome: str,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusService.Delete.Input(nome=nome)
    await StatusService.Delete.delete_status(payload, user_scope, db_session)
    return {"deleted": True}
