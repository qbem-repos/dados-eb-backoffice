import sys, pathlib
sys.path.append(str(pathlib.Path(__file__)).split("src", maxsplit=1)[0])

"""
Módulo de autenticação da API.

Modo atual: JWT direto via HTTPBearer
  - O cliente envia o token JWT no header: Authorization: Bearer <token>
  - O token é validado e o UserScope é extraído diretamente, sem depender de
    um endpoint de login interno.

Modo anterior (desativado): OAuth2PasswordBearer via JWTToken.get_current_user (shareds)
  - Dependia de um endpoint de login configurado em LOGIN_URL (shareds GetEnv).
  - Para reativar, substitua `get_current_user` pela versão comentada abaixo e
    restaure os imports de JWTToken nos endpoints.
"""

from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from shareds.services.api_utils.jwt_token import JWTToken
from shareds.services.app_security.user_scope import UserScope

# ---------------------------------------------------------------------------
# Modo atual: HTTPBearer — aceita o JWT diretamente no header Authorization
# ---------------------------------------------------------------------------

_http_bearer = HTTPBearer(
    scheme_name="JWT",
    description="Informe o token JWT no formato: Bearer <token>",
)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_http_bearer),
) -> UserScope:
    """
    Extrai e valida o JWT enviado diretamente no header Authorization.
    Retorna o UserScope com os dados do usuário autenticado.
    """
    token = credentials.credentials
    payload = JWTToken.validate_token(token)
    user_scope = UserScope.model_validate(payload.scopes)
    return user_scope


# ---------------------------------------------------------------------------
# Modo anterior (DESATIVADO): OAuth2PasswordBearer via JWTToken (shareds)
# Dependia de um endpoint de login configurado em LOGIN_URL nas env vars.
# ---------------------------------------------------------------------------

# from shareds.services.api_utils.jwt_token import JWTToken as _JWTToken
#
# async def get_current_user(
#     token: str = Depends(_JWTToken.oauth2_scheme),   # OAuth2PasswordBearer
# ) -> UserScope:
#     """
#     Valida o token obtido via fluxo OAuth2 (login endpoint).
#     Requer LOGIN_URL configurado nas variáveis de ambiente.
#     """
#     return await _JWTToken.get_current_user(token=token)
