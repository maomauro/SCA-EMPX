"""Schemas para personas. HU-01, HU-03."""
from pydantic import BaseModel


class PersonaRegistroResponse(BaseModel):
    id_persona: int
    nombre_completo: str
    documento: str
    estado: str
    calidad_embedding: float | None = None

    class Config:
        from_attributes = True
