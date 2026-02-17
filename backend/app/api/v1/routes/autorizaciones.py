"""Rutas autorizaciones de visita. HU-04."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Autorizacion
from backend.app.schemas.autorizacion import AutorizacionCreate, AutorizacionResponse
from backend.app.services.autorizacion_service import crear_autorizacion as svc_crear_autorizacion

router = APIRouter()


@router.get("/", response_model=list[AutorizacionResponse])
def listar_autorizaciones(db: Session = Depends(get_db)):
    """Lista todas las autorizaciones (vigentes, vencidas, canceladas)."""
    rows = db.query(Autorizacion).order_by(Autorizacion.fecha_inicio.desc()).all()
    return [AutorizacionResponse.model_validate(r) for r in rows]


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
    return AutorizacionResponse.model_validate(aut)
