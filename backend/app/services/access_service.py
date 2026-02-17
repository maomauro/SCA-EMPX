"""
Servicio de validación de acceso por reconocimiento facial (HU-05) y registro de evento (HU-06).
"""
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from backend.app.db.models import Persona, ReconocimientoFacial
from backend.app.services.event_service import register_entrada
from backend.app.ml.inference import (
    get_embedding_from_image,
    bytes_to_embedding,
    find_best_match,
)
from backend.app.core.config import SIMILARITY_THRESHOLD, FACE_DISTANCE_THRESHOLD


@dataclass
class ValidateAccessResult:
    allowed: bool
    person_id: int | None = None
    similarity: float | None = None
    reason: str = ""


def validate_access(
    db: Session, image_bytes: bytes, register_entrada_event: bool = True
) -> ValidateAccessResult:
    """
    Valida acceso por imagen facial.
    Si hay coincidencia y persona activa: allowed=True y, si register_entrada_event,
    se registra evento de entrada (HU-06). Si register_entrada_event=False solo identifica (para HU-07 salida).
    """
    result = _identify_person(db, image_bytes)
    if not result.allowed:
        return result
    if register_entrada_event:
        register_entrada(db, id_persona=result.person_id, similarity_score=result.similarity)
    return result


def _identify_person(db: Session, image_bytes: bytes) -> ValidateAccessResult:
    """Identifica persona por imagen (sin registrar evento). Usado por validate_access y register-exit."""
    embedding = get_embedding_from_image(image_bytes)
    if embedding is None:
        return ValidateAccessResult(allowed=False, reason="rostro_no_detectado")

    rows = (
        db.query(ReconocimientoFacial, Persona)
        .join(Persona, ReconocimientoFacial.id_persona == Persona.id_persona)
        .filter(ReconocimientoFacial.estado == "activo", Persona.estado == "activo")
        .all()
    )
    candidates = [(p.id_persona, bytes_to_embedding(r.embedding)) for r, p in rows]
    match = find_best_match(
        embedding, candidates, distance_threshold=FACE_DISTANCE_THRESHOLD
    )

    if match is None:
        return ValidateAccessResult(allowed=False, reason="persona_no_identificada")

    person_id, similarity = match
    if similarity < SIMILARITY_THRESHOLD:
        return ValidateAccessResult(allowed=False, reason="similitud_insuficiente")

    return ValidateAccessResult(
        allowed=True,
        person_id=person_id,
        similarity=round(similarity, 4),
        reason="acceso_permitido",
    )


