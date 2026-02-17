"""Rutas eventos entrada/salida. HU-06, HU-07, HU-08."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import RegistroAcceso, Persona
from backend.app.schemas.event import EventoListItem

router = APIRouter()

DEFAULT_LIMIT = 50
MAX_LIMIT = 100


@router.get("/", response_model=list[EventoListItem])
def listar_eventos(
    tipo: str | None = Query(None, description="ingreso | salida"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Lista eventos de acceso (registro_acceso). HU-06 opcional.
    Filtro opcional por tipo_movimiento (ingreso/salida). Paginación limit/offset.
    """
    q = (
        db.query(RegistroAcceso)
        .join(Persona, RegistroAcceso.id_persona == Persona.id_persona)
        .order_by(RegistroAcceso.fecha_hora.desc())
    )
    if tipo in ("ingreso", "entrada"):
        q = q.filter(RegistroAcceso.tipo_movimiento == "ingreso")
    elif tipo == "salida":
        q = q.filter(RegistroAcceso.tipo_movimiento == "salida")
    rows = q.offset(offset).limit(limit).all()
    return [
        EventoListItem(
            id_registro=r.id_registro,
            id_persona=r.id_persona,
            nombre_completo=r.persona.nombre_completo if r.persona else None,
            tipo_movimiento=r.tipo_movimiento,
            fecha_hora=r.fecha_hora,
            resultado=r.resultado,
            similarity_score=r.similarity_score,
            metodo_identificacion=r.metodo_identificacion,
        )
        for r in rows
    ]


@router.post("/exit")
def registrar_salida():
    return {"message": "Registro de salida (por implementar)"}
