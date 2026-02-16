"""Rutas validación de acceso. HU-05."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.services.access_service import validate_access, ValidateAccessResult

router = APIRouter()


class ValidateAccessResponse(BaseModel):
    allowed: bool
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
