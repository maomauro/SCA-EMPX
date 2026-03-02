"""Rutas validación de acceso. HU-05, HU-07."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.services.access_service import validate_access, ValidateAccessResult
from backend.app.services.event_service import register_salida

router = APIRouter()


class ValidateAccessResponse(BaseModel):
    allowed: bool
    person_id: int | None = None
    similarity: float | None = None
    reason: str


class RegisterExitResponse(BaseModel):
    registered: bool
    person_id: int | None = None
    similarity: float | None = None
    reason: str


@router.post("/validate", response_model=ValidateAccessResponse)
def validar_acceso(
    file: UploadFile = File(..., description="Imagen con un rostro (JPEG/PNG)"),
    db: Session = Depends(get_db),
):
    """
    Valida acceso por reconocimiento facial.
    Envía una imagen con un único rostro; retorna allowed, person_id (si hay match) y reason.
    Si allowed=true se registra el evento de entrada (HU-06).
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (JPEG, PNG, etc.)")

    image_bytes = file.file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Imagen vacía")

    result: ValidateAccessResult = validate_access(db, image_bytes)
    return ValidateAccessResponse(
        allowed=result.allowed,
        person_id=result.person_id,
        similarity=result.similarity,
        reason=result.reason,
    )


@router.post("/register-exit", response_model=RegisterExitResponse)
def registrar_salida_endpoint(
    file: UploadFile = File(..., description="Imagen con un rostro para registrar salida (JPEG/PNG)"),
    db: Session = Depends(get_db),
):
    """
    Registra evento de salida por reconocimiento facial (HU-07).
    Envía una imagen con un único rostro; se identifica a la persona y se registra la salida.
    Retorna registered=true y person_id si hubo identificación correcta.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (JPEG, PNG, etc.)")

    image_bytes = file.file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Imagen vacía")

    result = validate_access(db, image_bytes, register_entrada_event=False)
    if not result.allowed:
        return RegisterExitResponse(
            registered=False,
            person_id=None,
            similarity=result.similarity,
            reason=result.reason,
        )

    register_salida(
        db,
        id_persona=result.person_id,
        similarity_score=result.similarity,
    )
    return RegisterExitResponse(
        registered=True,
        person_id=result.person_id,
        similarity=result.similarity,
        reason="salida_registrada",
    )
