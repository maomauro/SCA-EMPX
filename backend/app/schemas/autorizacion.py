"""Schemas para autorizaciones de visita. HU-04."""
from datetime import datetime
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

    class Config:
        from_attributes = True
