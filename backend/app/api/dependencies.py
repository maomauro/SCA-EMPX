"""
Dependencias inyectables: sesión BD y usuario actual (auth).
"""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import UsuarioSistema
from backend.app.core.security import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user_optional(
    db: Annotated[Session, Depends(get_db)],
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> UsuarioSistema | None:
    """Obtiene el usuario actual si envía token válido; si no, retorna None."""
    if not credentials:
        return None
    payload = decode_access_token(credentials.credentials)
    if not payload or "sub" not in payload:
        return None
    user_id = payload["sub"]
    try:
        user_id = int(user_id)
    except ValueError:
        return None
    user = db.query(UsuarioSistema).filter(UsuarioSistema.id_usuario == user_id).first()
    if not user or user.estado != "activo":
        return None
    return user


def get_current_user(
    user: Annotated[UsuarioSistema | None, Depends(get_current_user_optional)],
) -> UsuarioSistema:
    """Exige usuario autenticado; 401 si no hay token o es inválido."""
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No autenticado o token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def require_admin(
    user: Annotated[UsuarioSistema, Depends(get_current_user)],
) -> UsuarioSistema:
    """Exige usuario autenticado con rol admin; 403 si no es admin. HU-09."""
    if user.rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol administrador",
        )
    return user
