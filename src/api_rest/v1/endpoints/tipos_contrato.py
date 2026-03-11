import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.app_security.user_scope import UserScope
from src.api_rest.auth import get_current_user
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.tipo_contrato import TipoContratoService


router = APIRouter(tags=["Tipos de Contrato"], prefix="/tipos-contrato")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=TipoContratoService.Create.Output)
async def create_tipo_contrato(
    data: TipoContratoService.Create.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await TipoContratoService.Create.create_tipo_contrato(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, TipoContratoService.Create.Output)


@router.get("/{nome}", response_model=TipoContratoService.Read.Output)
async def get_tipo_contrato(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoContratoService.Read.Input(nome=nome)
    model = await TipoContratoService.Read.get_tipo_contrato(payload, user_scope, db_session)
    return _to_output(model, TipoContratoService.Read.Output)


@router.get("", response_model=List[TipoContratoService.List.Input])
async def list_tipos_contrato(
    nome: str | None = None,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoContratoService.List.Input(nome=nome)
    items = await TipoContratoService.List.list_tipos_contrato(payload, user_scope, db_session)
    return [_to_output(item, TipoContratoService.List.Input) for item in items]


@router.put("/{nome}", response_model=TipoContratoService.Update.Output)
async def update_tipo_contrato(
    nome: str,
    data: TipoContratoService.Update.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoContratoService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await TipoContratoService.Update.update_tipo_contrato(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, TipoContratoService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_tipo_contrato(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = TipoContratoService.Delete.Input(nome=nome)
    await TipoContratoService.Delete.delete_tipo_contrato(payload, user_scope, db_session)
    return {"deleted": True}
