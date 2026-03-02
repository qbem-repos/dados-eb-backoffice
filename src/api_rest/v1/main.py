import sys
import pathlib

from fastapi import FastAPI

sys.path.append(str(pathlib.Path(__file__).resolve().parents[3]))

from src.api_rest.v1.endpoints import (
	operadoras,
	produtos,
	tipos_contrato,
	processos,
	tipos_rpa,
	status,
	retencao_carteirinhas,
	formas_operacao,
	status_acessos,
	rpas,
)

app = FastAPI(title="Backoffice EB API", version="v1")

app.include_router(operadoras.router)
app.include_router(produtos.router)
app.include_router(tipos_contrato.router)
app.include_router(processos.router)
app.include_router(tipos_rpa.router)
app.include_router(status.router)
app.include_router(retencao_carteirinhas.router)
app.include_router(formas_operacao.router)
app.include_router(status_acessos.router)
app.include_router(rpas.router)
