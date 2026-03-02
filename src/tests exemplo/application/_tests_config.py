import sys
import pathlib
from dataclasses import dataclass
from typing import List, Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

sys.path.append(str(pathlib.Path(__file__)).split("tests")[0])

from src.data.db_plataforma.models.contas import (
    CategoriaModel,
    CorretoraModel,
    ModuloModel,
    PerfilModel,
    UsuarioModel,
)
from shareds.services.app_security.passwords import hash_password
from shareds.services.app_security.user_scope import UserScope


def make_uuid(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex}"


def validate_output(output_model, result):
    return output_model.model_validate(result, from_attributes=True)


def build_usuario_output_payload(user: UsuarioModel) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "active": user.active,
        "super_admin": user.super_admin,
        "corretora_uuid": user.corretora_uuid,
        "estipulante_uuid": user.estipulante_especifica,
        "perfil_uuid": user.perfil_uuid,
        "usuario_categoria_uuid": user.user_categoria_uuid,
    }


def build_perfil_output_payload(perfil: PerfilModel) -> dict:
    return {
        "uuid": perfil.uuid,
        "modulo_uuids": [modulo.uuid for modulo in perfil.modulos],
    }


@dataclass
class BaseTestData:
    corretora_uuid: str
    categoria_uuid: str
    modulo_uuid: str
    perfil_uuid: str
    admin_user_id: int
    admin_email: str
    admin_password: str


async def create_base_data(session: AsyncSession) -> BaseTestData:
    corretora_uuid = make_uuid("corretora")
    categoria_uuid = make_uuid("categoria")
    modulo_uuid = make_uuid("modulo")
    perfil_uuid = make_uuid("perfil")
    admin_email = f"admin_{uuid4().hex}@test.local"
    admin_password = "Senha@12345"

    corretora = CorretoraModel(uuid=corretora_uuid, estipulantes=[], id_corretora_eb=None)
    categoria = CategoriaModel(uuid=categoria_uuid)
    modulo = ModuloModel(uuid=modulo_uuid)
    perfil = PerfilModel(uuid=perfil_uuid)
    perfil.modulos = [modulo]

    admin_user = UsuarioModel(
        name="Admin Teste",
        email=admin_email,
        hashed_pass=hash_password(admin_password),
        active=True,
        super_admin=True,
        corretora_uuid=corretora_uuid,
        perfil_uuid=perfil_uuid,
        user_categoria_uuid=categoria_uuid,
    )

    session.add_all([corretora, categoria, modulo, perfil, admin_user])
    await session.commit()
    await session.refresh(admin_user)

    return BaseTestData(
        corretora_uuid=corretora_uuid,
        categoria_uuid=categoria_uuid,
        modulo_uuid=modulo_uuid,
        perfil_uuid=perfil_uuid,
        admin_user_id=admin_user.id,
        admin_email=admin_email,
        admin_password=admin_password,
    )


def build_superadmin_scope(data: BaseTestData, ativo: bool = True) -> UserScope:
    return UserScope(
        user_id=data.admin_user_id,
        nome="Admin Teste",
        email=data.admin_email,
        corretora=data.corretora_uuid,
        estipulante=None,
        ativo=ativo,
        superadmin=True,
        perfil=data.perfil_uuid,
        modulos=[data.modulo_uuid],
        categoria=data.categoria_uuid,
    )


async def cleanup_base_data(session: AsyncSession, data: BaseTestData) -> None:
    result = await session.execute(select(UsuarioModel).where(UsuarioModel.email == data.admin_email))
    user = result.unique().scalars().one_or_none()
    if user is not None:
        await session.delete(user)
        await session.commit()

    result = await session.execute(select(PerfilModel).where(PerfilModel.uuid == data.perfil_uuid))
    perfil = result.unique().scalars().one_or_none()
    if perfil is not None:
        perfil.modulos = []
        await session.commit()
        await session.delete(perfil)
        await session.commit()

    result = await session.execute(select(ModuloModel).where(ModuloModel.uuid == data.modulo_uuid))
    modulo = result.scalars().one_or_none()
    if modulo is not None:
        await session.delete(modulo)
        await session.commit()

    result = await session.execute(select(CategoriaModel).where(CategoriaModel.uuid == data.categoria_uuid))
    categoria = result.scalars().one_or_none()
    if categoria is not None:
        await session.delete(categoria)
        await session.commit()

    result = await session.execute(select(CorretoraModel).where(CorretoraModel.uuid == data.corretora_uuid))
    corretora = result.scalars().one_or_none()
    if corretora is not None:
        await session.delete(corretora)
        await session.commit()


async def create_corretora(session: AsyncSession, uuid: Optional[str] = None) -> CorretoraModel:
    model = CorretoraModel(uuid=uuid or make_uuid("corretora"), estipulantes=[], id_corretora_eb=None)
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_corretora(session: AsyncSession, uuid: str) -> None:
    result = await session.execute(select(CorretoraModel).where(CorretoraModel.uuid == uuid))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_categoria(session: AsyncSession, uuid: Optional[str] = None) -> CategoriaModel:
    model = CategoriaModel(uuid=uuid or make_uuid("categoria"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_categoria(session: AsyncSession, uuid: str) -> None:
    result = await session.execute(select(CategoriaModel).where(CategoriaModel.uuid == uuid))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_modulo(session: AsyncSession, uuid: Optional[str] = None) -> ModuloModel:
    model = ModuloModel(uuid=uuid or make_uuid("modulo"))
    session.add(model)
    await session.commit()
    await session.refresh(model)
    return model


async def delete_modulo(session: AsyncSession, uuid: str) -> None:
    result = await session.execute(select(ModuloModel).where(ModuloModel.uuid == uuid))
    model = result.scalars().one_or_none()
    if model is not None:
        await session.delete(model)
        await session.commit()


async def create_perfil(
    session: AsyncSession,
    uuid: Optional[str] = None,
    modulo_uuids: Optional[List[str]] = None,
) -> PerfilModel:
    perfil = PerfilModel(uuid=uuid or make_uuid("perfil"))
    if modulo_uuids:
        result = await session.execute(select(ModuloModel).where(ModuloModel.uuid.in_(modulo_uuids)))
        perfil.modulos = result.scalars().all()
    session.add(perfil)
    await session.commit()
    await session.refresh(perfil)
    return perfil


async def delete_perfil(session: AsyncSession, uuid: str) -> None:
    result = await session.execute(select(PerfilModel).where(PerfilModel.uuid == uuid))
    perfil = result.unique().scalars().one_or_none()
    if perfil is not None:
        perfil.modulos = []
        await session.commit()
        await session.delete(perfil)
        await session.commit()


async def create_user(
    session: AsyncSession,
    *,
    email: Optional[str] = None,
    password: str = "Senha@12345",
    corretora_uuid: Optional[str] = None,
    perfil_uuid: Optional[str] = None,
    categoria_uuid: Optional[str] = None,
    active: bool = True,
    super_admin: bool = False,
) -> UsuarioModel:
    user = UsuarioModel(
        name="Usuario Teste",
        email=email or f"user_{uuid4().hex}@test.local",
        hashed_pass=hash_password(password),
        active=active,
        super_admin=super_admin,
        corretora_uuid=corretora_uuid,
        perfil_uuid=perfil_uuid,
        user_categoria_uuid=categoria_uuid,
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def delete_user(session: AsyncSession, user_id: int) -> None:
    result = await session.execute(select(UsuarioModel).where(UsuarioModel.id == user_id))
    user = result.unique().scalars().one_or_none()
    if user is not None:
        await session.delete(user)
        await session.commit()
