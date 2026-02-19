"""
Endpoints de gestión de visitas — historial de visitantes y contratistas.

Una visita representa el ingreso de una persona no-empleada a las
instalaciones. Se crea al iniciar la visita, queda abierta (``fecha_salida
= NULL``) hasta que el individuo sale, momento en que se registra la hora
de salida ya sea manualmente (este endpoint) o automáticamente por el
pipeline de reconocimiento facial (``acceso.py``).

Rutas:
    POST   /visitas/                  → Crea una visita y registra entrada automática.
    GET    /visitas/                  → Lista visitas (filtro opcional por persona).
    PATCH  /visitas/{id}/salida       → Registra la hora de salida.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import numpy as np

from backend.app.db.database import get_db
from backend.app.db.models import Persona, Visita, Registro
from backend.app.ml.face_model import embedding_to_bytes

router = APIRouter()


class VisitaCreate(BaseModel):
    """Schema de entrada para registrar una visita.

    Attributes:
        id_persona: FK a la persona que realiza la visita.
        motivo:     Descripción del propósito de la visita.
    """
    id_persona: int
    motivo: str


@router.post("/")
def crear_visita(body: VisitaCreate, db: Session = Depends(get_db)):
    """Registra una nueva visita y genera automáticamente un acceso de entrada.

    Crea un registro en ``visitas`` con ``fecha_salida = NULL`` y añade
    un registro de acceso de tipo ``'entrada'`` en ``registros`` con
    embedding vacío (cero), ya que la visita se creó manualmente.

    Args:
        body: Datos de la visita (id_persona y motivo).
        db:   Sesión de base de datos.

    Returns:
        Diccionario con los datos de la visita creada.

    Raises:
        HTTPException: 404 si la persona no existe.
        HTTPException: 400 si la persona es empleado (las visitas son solo
                       para visitantes y contratistas).
    """
    persona = db.query(Persona).filter(Persona.id_persona == body.id_persona).first()
    if not persona:
        raise HTTPException(404, "Persona no encontrada.")
    if persona.tipo_persona and persona.tipo_persona.es_empleado:
        raise HTTPException(400, "Las visitas son solo para visitantes y contratistas.")

    v = Visita(id_persona=body.id_persona, motivo=body.motivo.strip())
    db.add(v)

    # Registrar acceso de entrada automático al iniciar la visita
    embedding_vacio = embedding_to_bytes(np.zeros(512, dtype=np.float32))
    reg = Registro(
        id_persona=body.id_persona,
        evento="acceso",
        tipo_acceso="entrada",
        embedding_facial=embedding_vacio,
        similitud=None,
    )
    db.add(reg)

    db.commit()
    db.refresh(v)
    return {
        "id_visita":  v.id_visita,
        "id_persona": v.id_persona,
        "nombres":    persona.nombres,
        "motivo":     v.motivo,
        "fecha":      v.fecha,
    }


@router.get("/")
def listar_visitas(id_persona: Optional[int] = None, db: Session = Depends(get_db)):
    """Lista el historial de visitas ordenado por fecha descendente.

    Args:
        id_persona: Si se proporciona, filtra las visitas de esa persona.
        db:         Sesión de base de datos.

    Returns:
        Lista de hasta 100 visitas con ``fecha_salida=None`` si aún están activas.
    """
    q = db.query(Visita).join(Persona)
    if id_persona:
        q = q.filter(Visita.id_persona == id_persona)
    visitas = q.order_by(Visita.fecha.desc()).limit(100).all()
    return [
        {
            "id_visita":  v.id_visita,
            "id_persona": v.id_persona,
            "nombres":    v.persona.nombres,
            "motivo":     v.motivo,
            "fecha":      v.fecha,
            "fecha_salida": v.fecha_salida,
        }
        for v in visitas
    ]


@router.patch("/{id_visita}/salida")
def registrar_salida_visita(id_visita: int, db: Session = Depends(get_db)):
    """Registra manualmente la hora de salida de una visita activa.

    Args:
        id_visita: Identificador de la visita a cerrar.
        db:        Sesión de base de datos.

    Returns:
        ``{"ok": True, "fecha_salida": <timestamp UTC>}``.

    Raises:
        HTTPException: 404 si la visita no existe.
    """
    v = db.query(Visita).filter(Visita.id_visita == id_visita).first()
    if not v:
        raise HTTPException(404, "Visita no encontrada.")
    v.fecha_salida = datetime.now(timezone.utc)
    db.commit()
    return {"ok": True, "fecha_salida": v.fecha_salida}
