import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.app_security.user_scope import UserScope
from src.api_rest.auth import get_current_user
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.operadora import OperadoraService


router = APIRouter(tags=["Operadoras"], prefix="/operadoras")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=OperadoraService.Create.Output)
async def create_operadora(
    data: OperadoraService.Create.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await OperadoraService.Create.create_operadora(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, OperadoraService.Create.Output)


@router.get("/{nome}", response_model=OperadoraService.Read.Output)
async def get_operadora(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = OperadoraService.Read.Input(nome=nome)
    model = await OperadoraService.Read.get_operadora(payload, user_scope, db_session)
    return _to_output(model, OperadoraService.Read.Output)


@router.get("", response_model=List[OperadoraService.List.Input])
async def list_operadoras(
    nome: str | None = None,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = OperadoraService.List.Input(nome=nome)
    items = await OperadoraService.List.list_operadoras(payload, user_scope, db_session)
    return [_to_output(item, OperadoraService.List.Input) for item in items]


@router.put("/{nome}", response_model=OperadoraService.Update.Output)
async def update_operadora(
    nome: str,
    data: OperadoraService.Update.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = OperadoraService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await OperadoraService.Update.update_operadora(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, OperadoraService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_operadora(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = OperadoraService.Delete.Input(nome=nome)
    await OperadoraService.Delete.delete_operadora(payload, user_scope, db_session)
    return {"deleted": True}
