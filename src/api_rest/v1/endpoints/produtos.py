import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from shareds.services.app_security.user_scope import UserScope
from src.api_rest.auth import get_current_user
from src.data.db_backoffice_eb.db_session import get_async_db_session_dependency
from src.application.rpas.produto import ProdutoService


router = APIRouter(tags=["Produtos"], prefix="/produtos")


def _to_output(model, output_cls):
    return output_cls(**{field: getattr(model, field) for field in output_cls.model_fields})


@router.post("", response_model=ProdutoService.Create.Output)
async def create_produto(
    data: ProdutoService.Create.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    model = await ProdutoService.Create.create_produto(
        data,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, ProdutoService.Create.Output)


@router.get("/{nome}", response_model=ProdutoService.Read.Output)
async def get_produto(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProdutoService.Read.Input(nome=nome)
    model = await ProdutoService.Read.get_produto(payload, user_scope, db_session)
    return _to_output(model, ProdutoService.Read.Output)


@router.get("", response_model=List[ProdutoService.List.Input])
async def list_produtos(
    nome: str | None = None,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProdutoService.List.Input(nome=nome)
    items = await ProdutoService.List.list_produtos(payload, user_scope, db_session)
    return [_to_output(item, ProdutoService.List.Input) for item in items]


@router.put("/{nome}", response_model=ProdutoService.Update.Output)
async def update_produto(
    nome: str,
    data: ProdutoService.Update.Input,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProdutoService.Update.Input(
        nome_atual=nome,
        **data.model_dump(exclude_unset=True, exclude={"nome_atual"}),
    )
    model = await ProdutoService.Update.update_produto(
        payload,
        user_scope,
        db_session,
        user_id=getattr(user_scope, "user_id", None),
    )
    return _to_output(model, ProdutoService.Update.Output)


@router.delete("/{nome}", response_model=dict)
async def delete_produto(
    nome: str,
    user_scope: UserScope = Depends(get_current_user),
    db_session: AsyncSession = Depends(get_async_db_session_dependency),
):
    payload = ProdutoService.Delete.Input(nome=nome)
    await ProdutoService.Delete.delete_produto(payload, user_scope, db_session)
    return {"deleted": True}
