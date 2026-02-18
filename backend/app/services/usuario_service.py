"""
Servicio de usuarios del sistema. HU-09.
"""
from sqlalchemy.orm import Session

from backend.app.db.models import UsuarioSistema
from backend.app.core.security import get_password_hash


def crear_usuario(
    db: Session,
    nombre_usuario: str,
    password: str,
    rol: str = "recepcion",
) -> UsuarioSistema:
    """
    Crea un usuario del sistema. Lanza ValueError si nombre_usuario ya existe.
    """
    nombre = nombre_usuario.strip().lower()
    if not nombre:
        raise ValueError("nombre_usuario_vacio")
    if db.query(UsuarioSistema).filter(UsuarioSistema.nombre_usuario == nombre).first():
        raise ValueError("nombre_usuario_duplicado")
    roles_validos = ("admin", "rrhh", "recepcion", "seguridad")
    if rol not in roles_validos:
        raise ValueError("rol_invalido")
    user = UsuarioSistema(
        nombre_usuario=nombre,
        hash_password=get_password_hash(password),
        rol=rol,
        estado="activo",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
