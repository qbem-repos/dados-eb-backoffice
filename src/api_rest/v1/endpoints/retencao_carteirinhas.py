import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.app_security.user_scope import UserScope
from src.api_rest.auth import get_current_user
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.retencao_carteirinha import RetencaoCarteirinhaService


router = APIRouter(tags=["Retenções de Carteirinha"], prefix="/retencao-carteirinhas")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=RetencaoCarteirinhaService.Create.Output)
async def create_retencao_carteirinha(
    data: RetencaoCarteirinhaService.Create.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await RetencaoCarteirinhaService.Create.create_retencao_carteirinha(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, RetencaoCarteirinhaService.Create.Output)


@router.get("/{nome}", response_model=RetencaoCarteirinhaService.Read.Output)
async def get_retencao_carteirinha(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = RetencaoCarteirinhaService.Read.Input(nome=nome)
    model = await RetencaoCarteirinhaService.Read.get_retencao_carteirinha(payload, user_scope, db_session)
    return _to_output(model, RetencaoCarteirinhaService.Read.Output)


@router.get("", response_model=List[RetencaoCarteirinhaService.List.Input])
async def list_retencoes_carteirinha(
    nome: str | None = None,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = RetencaoCarteirinhaService.List.Input(nome=nome)
    items = await RetencaoCarteirinhaService.List.list_retencoes_carteirinha(payload, user_scope, db_session)
    return [_to_output(item, RetencaoCarteirinhaService.List.Input) for item in items]


@router.put("/{nome}", response_model=RetencaoCarteirinhaService.Update.Output)
async def update_retencao_carteirinha(
    nome: str,
    data: RetencaoCarteirinhaService.Update.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = RetencaoCarteirinhaService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await RetencaoCarteirinhaService.Update.update_retencao_carteirinha(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, RetencaoCarteirinhaService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_retencao_carteirinha(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = RetencaoCarteirinhaService.Delete.Input(nome=nome)
    await RetencaoCarteirinhaService.Delete.delete_retencao_carteirinha(payload, user_scope, db_session)
    return {"deleted": True}
