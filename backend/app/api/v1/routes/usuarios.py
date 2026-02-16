"""Rutas usuarios del sistema. HU-09."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.db.models import UsuarioSistema
from backend.app.core.security import verify_password, create_access_token
from backend.app.api.dependencies import get_current_user

router = APIRouter()


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """Login: usuario y contraseña → JWT."""
    user = db.query(UsuarioSistema).filter(UsuarioSistema.nombre_usuario == body.username).first()
    if not user or user.estado != "activo":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    if not verify_password(body.password, user.hash_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    token = create_access_token(subject=user.id_usuario)
    return TokenResponse(access_token=token)


@router.get("/")
def listar_usuarios(db: Session = Depends(get_db), _user: UsuarioSistema = Depends(get_current_user)):
    """Listar usuarios (requiere autenticación)."""
    return {"message": "Listado de usuarios (por implementar)"}


@router.post("/")
def crear_usuario(db: Session = Depends(get_db), _user: UsuarioSistema = Depends(get_current_user)):
    """Crear usuario (requiere autenticación)."""
    return {"message": "Crear usuario (por implementar)"}
