import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.api_utils.jwt_token import JWTToken
from shareds.services.app_security.user_scope import UserScope
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.processo import ProcessoService


router = APIRouter(tags=["Processos"], prefix="/processos")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=ProcessoService.Create.Output)
async def create_processo(
    data: ProcessoService.Create.Input,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await ProcessoService.Create.create_processo(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, ProcessoService.Create.Output)


@router.get("/{nome}", response_model=ProcessoService.Read.Output)
async def get_processo(
    nome: str,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProcessoService.Read.Input(nome=nome)
    model = await ProcessoService.Read.get_processo(payload, user_scope, db_session)
    return _to_output(model, ProcessoService.Read.Output)


@router.get("", response_model=List[ProcessoService.List.Input])
async def list_processos(
    nome: str | None = None,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProcessoService.List.Input(nome=nome)
    items = await ProcessoService.List.list_processos(payload, user_scope, db_session)
    return [_to_output(item, ProcessoService.List.Input) for item in items]


@router.put("/{nome}", response_model=ProcessoService.Update.Output)
async def update_processo(
    nome: str,
    data: ProcessoService.Update.Input,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProcessoService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await ProcessoService.Update.update_processo(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, ProcessoService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_processo(
    nome: str,
    user_scope: UserScope = Depends(JWTToken.get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProcessoService.Delete.Input(nome=nome)
    await ProcessoService.Delete.delete_processo(payload, user_scope, db_session)
    return {"deleted": True}
