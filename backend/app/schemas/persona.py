"""Schemas para personas. HU-01, HU-03, HU-10, HU-14."""
from datetime import datetime
from pydantic import BaseModel


class PersonaDentro(BaseModel):
    """Persona actualmente dentro (último evento = ingreso permitido). HU-14."""
    id_persona: int
    nombre_completo: str
    fecha_hora_entrada: datetime


class PersonaListItem(BaseModel):
    id_persona: int
    nombre_completo: str
    documento: str
    estado: str | None = None  # HU-02: incluido para listado con Desactivar/Activar

    class Config:
        from_attributes = True


class PersonaDetail(BaseModel):
    """Detalle de persona para edición. HU-10."""
    id_persona: int
    nombre_completo: str
    documento: str
    tipo_documento: str | None = None
    cargo: str | None = None
    area: str | None = None
    telefono: str | None = None
    email: str | None = None
    estado: str
    tipo: str  # empleado_propio | visitante_temporal

    class Config:
        from_attributes = True


class PersonaUpdate(BaseModel):
    """Campos editables de persona. HU-10. Todos opcionales; solo se actualizan los enviados."""
    nombre_completo: str | None = None
    cargo: str | None = None
    area: str | None = None
    telefono: str | None = None
    email: str | None = None
    estado: str | None = None  # activo | inactivo (compat HU-02)


class PersonaRegistroResponse(BaseModel):
    id_persona: int
    nombre_completo: str
    documento: str
    estado: str
    calidad_embedding: float | None = None

    class Config:
        from_attributes = True
