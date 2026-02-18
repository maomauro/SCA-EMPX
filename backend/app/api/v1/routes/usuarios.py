"""Rutas usuarios del sistema. HU-09."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.db.models import UsuarioSistema
from backend.app.core.security import verify_password, create_access_token
from backend.app.api.dependencies import get_current_user, require_admin
from backend.app.schemas.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdateEstado
from backend.app.services.usuario_service import crear_usuario as svc_crear_usuario

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


@router.get("/", response_model=list[UsuarioResponse])
def listar_usuarios(
    db: Session = Depends(get_db),
    _user: UsuarioSistema = Depends(get_current_user),
):
    """Listar usuarios del sistema (requiere autenticación)."""
    users = db.query(UsuarioSistema).order_by(UsuarioSistema.nombre_usuario).all()
    return [UsuarioResponse.model_validate(u) for u in users]


@router.post("/", response_model=UsuarioResponse)
def crear_usuario(
    body: UsuarioCreate,
    db: Session = Depends(get_db),
    _user: UsuarioSistema = Depends(require_admin),
):
    """Crear usuario (solo admin). nombre_usuario único; rol: admin, rrhh, recepcion, seguridad."""
    try:
        user = svc_crear_usuario(
            db,
            nombre_usuario=body.nombre_usuario,
            password=body.password,
            rol=body.rol or "recepcion",
        )
    except ValueError as e:
        msg = str(e)
        if msg == "nombre_usuario_duplicado":
            raise HTTPException(status_code=409, detail="Ya existe un usuario con ese nombre.")
        if msg == "nombre_usuario_vacio":
            raise HTTPException(status_code=400, detail="El nombre de usuario no puede estar vacío.")
        if msg == "rol_invalido":
            raise HTTPException(status_code=400, detail="Rol inválido. Use: admin, rrhh, recepcion, seguridad.")
        raise HTTPException(status_code=400, detail=msg)
    return UsuarioResponse.model_validate(user)


@router.patch("/{usuario_id:int}", response_model=UsuarioResponse)
def actualizar_estado_usuario(
    usuario_id: int,
    body: UsuarioUpdateEstado,
    db: Session = Depends(get_db),
    _user: UsuarioSistema = Depends(require_admin),
):
    """Activar o desactivar usuario (solo admin). estado: activo | inactivo."""
    if body.estado not in ("activo", "inactivo"):
        raise HTTPException(status_code=400, detail="estado debe ser 'activo' o 'inactivo'.")
    user = db.query(UsuarioSistema).filter(UsuarioSistema.id_usuario == usuario_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    user.estado = body.estado
    db.commit()
    db.refresh(user)
    return UsuarioResponse.model_validate(user)
