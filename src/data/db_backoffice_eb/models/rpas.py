import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src")[0])

from src.data.db_backoffice_eb.models._base_model import BaseModel
from shareds.services.app_security.user_scope import UserScope

from typing import List, Optional
from sqlalchemy import Column, Integer, BigInteger, UniqueConstraint, String, Date, DateTime, Text, ForeignKey, Boolean, Table, ARRAY, PrimaryKeyConstraint, Enum, Float, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, date

from typing import List

class OperadoraModel(BaseModel):
    __tablename__ = "operadoras"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    
class ProdutoModel(BaseModel):
    __tablename__ = "produtos"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "Saúde", "Vida", "Odonto"


class TipoContratoModel(BaseModel):
    __tablename__ = "tipos_contrato"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "PJ", "PME", "Adesão", "Individual"

class ProcessoModel(BaseModel):
    __tablename__ = "processos"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "Saúde", "Vida", "Odonto"

class TipoRPAModel(BaseModel):
    __tablename__ = "tipos_rpa"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "Faturamento", "Movimentação"

class StatusModel(BaseModel):
    __tablename__ = "status"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "Funcionando", "Manutenção", "Pausado", "Dep. Operadora"

class RetencaoCarteirinhaModel(BaseModel):
    __tablename__ = "retencao_carteirinhas"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "Automático", "Manual"

class FormaOperacaoModel(BaseModel):
    __tablename__ = "formas_operacao"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "Online", "Batch", "Híbrido", "Manual"

class StatusAcessosModel(BaseModel):
    __tablename__ = "status_acessos"
    __table_args__ = {"schema": "rpas"}

    nome: Mapped[str] = mapped_column(String, index=True, unique=True, primary_key=True)
    #Valores possíveis: "Ativo", "Pendente", "Bloqueado"

class RPAModel(BaseModel):
    __tablename__ = "rpas"
    __table_args__ = {"schema": "rpas"}

    id: Mapped[int] = mapped_column(Integer, index=True, unique=True, primary_key=True)
    nome: Mapped[str] = mapped_column(String, index=True, unique=True)
    operadora_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.operadoras.nome"))
    produto_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.produtos.nome"))
    tipo_contrato_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.tipos_contrato.nome"))
    processo_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.processos.nome"))
    tipo_rpa_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.tipos_rpa.nome"))
    status_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.status.nome"))
    status_detalhe: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status_last_update: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    retencao_carteirinha_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.retencao_carteirinhas.nome"))
    doc_baixa: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    forma_operacao_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.formas_operacao.nome"))
    status_acesso_nome: Mapped[str] = mapped_column(String, ForeignKey("rpas.status_acessos.nome"))
    status_acesso_detalhe: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    status_acesso_last_update: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)