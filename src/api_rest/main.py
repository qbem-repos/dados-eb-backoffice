import sys
import pathlib

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

sys.path.append(str(pathlib.Path(__file__).resolve().parents[2]))

from src.api_rest.v1.main import app as backoffice_app


description = """
<ul>
	<li><a href="/backoffice/v1/docs">Backoffice EB API</a></li>
</ul>
"""

app = FastAPI(title="Backoffice EB API", version="v1", description=description)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/backoffice/v1", backoffice_app)
