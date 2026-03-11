import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.app_security.user_scope import UserScope
from src.api_rest.auth import get_current_user
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.forma_operacao import FormaOperacaoService


router = APIRouter(tags=["Formas de Operação"], prefix="/formas-operacao")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=FormaOperacaoService.Create.Output)
async def create_forma_operacao(
    data: FormaOperacaoService.Create.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await FormaOperacaoService.Create.create_forma_operacao(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, FormaOperacaoService.Create.Output)


@router.get("/{nome}", response_model=FormaOperacaoService.Read.Output)
async def get_forma_operacao(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = FormaOperacaoService.Read.Input(nome=nome)
    model = await FormaOperacaoService.Read.get_forma_operacao(payload, user_scope, db_session)
    return _to_output(model, FormaOperacaoService.Read.Output)


@router.get("", response_model=List[FormaOperacaoService.List.Input])
async def list_formas_operacao(
    nome: str | None = None,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = FormaOperacaoService.List.Input(nome=nome)
    items = await FormaOperacaoService.List.list_formas_operacao(payload, user_scope, db_session)
    return [_to_output(item, FormaOperacaoService.List.Input) for item in items]


@router.put("/{nome}", response_model=FormaOperacaoService.Update.Output)
async def update_forma_operacao(
    nome: str,
    data: FormaOperacaoService.Update.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = FormaOperacaoService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await FormaOperacaoService.Update.update_forma_operacao(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, FormaOperacaoService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_forma_operacao(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = FormaOperacaoService.Delete.Input(nome=nome)
    await FormaOperacaoService.Delete.delete_forma_operacao(payload, user_scope, db_session)
    return {"deleted": True}
