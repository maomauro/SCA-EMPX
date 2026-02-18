"""Schemas para personas. HU-01, HU-03."""
from pydantic import BaseModel


class PersonaListItem(BaseModel):
    id_persona: int
    nombre_completo: str
    documento: str
    estado: str | None = None  # HU-02: incluido para listado con Desactivar/Activar

    class Config:
        from_attributes = True


class PersonaUpdateEstado(BaseModel):
    estado: str  # activo | inactivo


class PersonaRegistroResponse(BaseModel):
    id_persona: int
    nombre_completo: str
    documento: str
    estado: str
    calidad_embedding: float | None = None

    class Config:
        from_attributes = True
