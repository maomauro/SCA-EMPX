"""
Servicio de validación de acceso por reconocimiento facial (HU-05) y registro de evento (HU-06).
"""
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from backend.app.db.models import Persona, ReconocimientoFacial, RegistroAcceso
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


def validate_access(db: Session, image_bytes: bytes) -> ValidateAccessResult:
    """
    Valida acceso por imagen facial.
    Si hay coincidencia y persona activa: allowed=True y se registra evento de entrada.
    """
    embedding = get_embedding_from_image(image_bytes)
    if embedding is None:
        return ValidateAccessResult(allowed=False, reason="rostro_no_detectado")

    # Obtener todos los embeddings activos (persona activa + reconocimiento activo)
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

    # Registrar evento de entrada (HU-06)
    _register_entrada(db, person_id=person_id, similarity_score=similarity)
    return ValidateAccessResult(
        allowed=True,
        person_id=person_id,
        similarity=round(similarity, 4),
        reason="acceso_permitido",
    )


def _register_entrada(db: Session, person_id: int, similarity_score: float) -> None:
    """Registra evento de entrada en registro_acceso (HU-06)."""
    reg = RegistroAcceso(
        id_persona=person_id,
        tipo_movimiento="ingreso",
        metodo_identificacion="reconocimiento_facial",
        resultado="permitido",
        similarity_score=similarity_score,
    )
    db.add(reg)
    db.commit()
