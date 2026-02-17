"""Schemas para eventos de acceso (registro_acceso). HU-06, HU-08."""
from datetime import datetime
from pydantic import BaseModel


class EventoListItem(BaseModel):
    id_registro: int
    id_persona: int
    nombre_completo: str | None = None
    tipo_movimiento: str
    fecha_hora: datetime
    resultado: str
    similarity_score: float | None = None
    metodo_identificacion: str

    class Config:
        from_attributes = True
