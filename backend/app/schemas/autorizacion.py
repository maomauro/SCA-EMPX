"""Schemas para autorizaciones de visita. HU-04, HU-13."""
from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class AutorizacionCreate(BaseModel):
    id_persona: int
    fecha_inicio: datetime
    fecha_fin: datetime


class AutorizacionResponse(BaseModel):
    id_autorizacion: int
    id_persona: int
    fecha_inicio: datetime
    fecha_fin: datetime
    estado: str
    motivo_revocacion: str | None = None
    nombre_completo: str | None = None  # HU-13: para listado con persona

    class Config:
        from_attributes = True


class AutorizacionRevocar(BaseModel):
    """Cuerpo para revocar una autorización. HU-13."""
    estado: Literal["revocada"] = "revocada"
    motivo: str | None = None
