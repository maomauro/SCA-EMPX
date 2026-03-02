"""Schemas para usuarios del sistema. HU-09."""
from datetime import datetime
from pydantic import BaseModel


class UsuarioCreate(BaseModel):
    nombre_usuario: str
    password: str
    rol: str = "recepcion"  # admin | rrhh | recepcion | seguridad


class UsuarioResponse(BaseModel):
    id_usuario: int
    nombre_usuario: str
    rol: str
    estado: str
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class UsuarioUpdateEstado(BaseModel):
    estado: str  # activo | inactivo
