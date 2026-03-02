"""
Servicio de autorizaciones de visita. HU-04.
"""
from datetime import datetime
from sqlalchemy.orm import Session

from backend.app.db.models import Autorizacion, Persona, TipoPersona


def crear_autorizacion(
    db: Session,
    id_persona: int,
    fecha_inicio: datetime,
    fecha_fin: datetime,
) -> Autorizacion:
    """
    Crea una autorización vigente para un visitante.
    Lanza ValueError si la persona no existe, no es visitante, o fechas inválidas.
    """
    if fecha_fin <= fecha_inicio:
        raise ValueError("fecha_fin_debe_ser_posterior")

    persona = db.query(Persona).filter(Persona.id_persona == id_persona).first()
    if not persona:
        raise ValueError("persona_no_encontrada")

    tipo = db.query(TipoPersona).filter(TipoPersona.id_tipo_persona == persona.id_tipo_persona).first()
    if not tipo or tipo.nombre_tipo != "visitante_temporal":
        raise ValueError("solo_visitantes")

    if persona.estado != "activo":
        raise ValueError("persona_inactiva")

    aut = Autorizacion(
        id_persona=id_persona,
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        estado="vigente",
    )
    db.add(aut)
    db.commit()
    db.refresh(aut)
    return aut
