"""Schemas para eventos de acceso (registro_acceso). HU-06, HU-08, HU-11."""
from datetime import datetime
from pydantic import BaseModel


class DashboardEstadisticas(BaseModel):
    """Métricas para dashboard. HU-11."""
    total_dentro: int
    accesos_hoy: int
    denegaciones_hoy: int


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
