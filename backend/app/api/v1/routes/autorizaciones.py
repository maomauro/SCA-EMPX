"""Rutas autorizaciones de visita. HU-04, HU-13."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Autorizacion
from backend.app.schemas.autorizacion import AutorizacionCreate, AutorizacionResponse, AutorizacionRevocar
from backend.app.services.autorizacion_service import crear_autorizacion as svc_crear_autorizacion

router = APIRouter()


def _autorizacion_to_response(r) -> AutorizacionResponse:
    return AutorizacionResponse(
        id_autorizacion=r.id_autorizacion,
        id_persona=r.id_persona,
        fecha_inicio=r.fecha_inicio,
        fecha_fin=r.fecha_fin,
        estado=r.estado,
        motivo_revocacion=getattr(r, "motivo_revocacion", None),
        nombre_completo=r.persona.nombre_completo if r.persona else None,
    )


@router.get("/", response_model=list[AutorizacionResponse])
def listar_autorizaciones(
    estado: str | None = Query(None, description="vigente | vencida | cancelada | revocada; sin valor = todas"),
    db: Session = Depends(get_db),
):
    """Lista autorizaciones. HU-13: use estado=vigente para listar solo activas."""
    query = db.query(Autorizacion).order_by(Autorizacion.fecha_inicio.desc())
    if estado and estado.strip() in ("vigente", "vencida", "cancelada", "revocada"):
        query = query.filter(Autorizacion.estado == estado.strip())
    rows = query.all()
    return [_autorizacion_to_response(r) for r in rows]


@router.post("/", response_model=AutorizacionResponse)
def crear_autorizacion(body: AutorizacionCreate, db: Session = Depends(get_db)):
    """
    Crea una autorización de visita vigente para un visitante.
    id_persona debe ser un visitante activo. fecha_fin debe ser posterior a fecha_inicio.
    """
    try:
        aut = svc_crear_autorizacion(
            db,
            id_persona=body.id_persona,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
        )
    except ValueError as e:
        msg = str(e)
        if msg == "fecha_fin_debe_ser_posterior":
            raise HTTPException(status_code=400, detail="La fecha fin debe ser posterior a la fecha inicio.")
        if msg == "persona_no_encontrada":
            raise HTTPException(status_code=404, detail="Persona no encontrada.")
        if msg == "solo_visitantes":
            raise HTTPException(status_code=400, detail="Solo se pueden crear autorizaciones para visitantes.")
        if msg == "persona_inactiva":
            raise HTTPException(status_code=400, detail="La persona está inactiva.")
        raise HTTPException(status_code=400, detail=msg)
    return _autorizacion_to_response(aut)


@router.patch("/{autorizacion_id:int}", response_model=AutorizacionResponse)
def revocar_autorizacion(
    autorizacion_id: int,
    body: AutorizacionRevocar,
    db: Session = Depends(get_db),
):
    """
    Revoca una autorización vigente. HU-13. Solo se puede revocar si estado actual es vigente.
    """
    aut = db.query(Autorizacion).filter(Autorizacion.id_autorizacion == autorizacion_id).first()
    if not aut:
        raise HTTPException(status_code=404, detail="Autorización no encontrada.")
    if aut.estado != "vigente":
        raise HTTPException(status_code=400, detail="Solo se puede revocar una autorización vigente.")
    aut.estado = "revocada"
    aut.motivo_revocacion = (body.motivo or "").strip() or None
    db.commit()
    db.refresh(aut)
    return _autorizacion_to_response(aut)
