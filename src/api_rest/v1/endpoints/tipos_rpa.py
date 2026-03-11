import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.app_security.user_scope import UserScope
from src.api_rest.auth import get_current_user
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.tipo_rpa import TipoRPAService


router = APIRouter(tags=["Tipos de RPA"], prefix="/tipos-rpa")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=TipoRPAService.Create.Output)
async def create_tipo_rpa(
    data: TipoRPAService.Create.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await TipoRPAService.Create.create_tipo_rpa(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, TipoRPAService.Create.Output)


@router.get("/{nome}", response_model=TipoRPAService.Read.Output)
async def get_tipo_rpa(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoRPAService.Read.Input(nome=nome)
    model = await TipoRPAService.Read.get_tipo_rpa(payload, user_scope, db_session)
    return _to_output(model, TipoRPAService.Read.Output)


@router.get("", response_model=List[TipoRPAService.List.Input])
async def list_tipos_rpa(
    nome: str | None = None,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoRPAService.List.Input(nome=nome)
    items = await TipoRPAService.List.list_tipos_rpa(payload, user_scope, db_session)
    return [_to_output(item, TipoRPAService.List.Input) for item in items]


@router.put("/{nome}", response_model=TipoRPAService.Update.Output)
async def update_tipo_rpa(
    nome: str,
    data: TipoRPAService.Update.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoRPAService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await TipoRPAService.Update.update_tipo_rpa(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, TipoRPAService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_tipo_rpa(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoRPAService.Delete.Input(nome=nome)
    await TipoRPAService.Delete.delete_tipo_rpa(payload, user_scope, db_session)
    return {"deleted": True}
