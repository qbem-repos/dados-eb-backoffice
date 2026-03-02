import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.api_utils.jwt_token import JWTToken
from shareds.services.app_security.user_scope import UserScope
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.status_acessos import StatusAcessosService


router = APIRouter(tags=["Status de Acessos"], prefix="/status-acessos")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=StatusAcessosService.Create.Output)
async def create_status_acessos(
    data: StatusAcessosService.Create.Input,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await StatusAcessosService.Create.create_status_acessos(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, StatusAcessosService.Create.Output)


@router.get("/{nome}", response_model=StatusAcessosService.Read.Output)
async def get_status_acessos(
    nome: str,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusAcessosService.Read.Input(nome=nome)
    model = await StatusAcessosService.Read.get_status_acessos(payload, user_scope, db_session)
    return _to_output(model, StatusAcessosService.Read.Output)


@router.get("", response_model=List[StatusAcessosService.List.Input])
async def list_status_acessos(
    nome: str | None = None,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusAcessosService.List.Input(nome=nome)
    items = await StatusAcessosService.List.list_status_acessos(payload, user_scope, db_session)
    return [_to_output(item, StatusAcessosService.List.Input) for item in items]


@router.put("/{nome}", response_model=StatusAcessosService.Update.Output)
async def update_status_acessos(
    nome: str,
    data: StatusAcessosService.Update.Input,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusAcessosService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await StatusAcessosService.Update.update_status_acessos(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, StatusAcessosService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_status_acessos(
    nome: str,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = StatusAcessosService.Delete.Input(nome=nome)
    await StatusAcessosService.Delete.delete_status_acessos(payload, user_scope, db_session)
    return {"deleted": True}
