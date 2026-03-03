"""
Servicio de validación de acceso por reconocimiento facial (HU-05) y registro de evento (HU-06).
"""
from dataclasses import dataclass
from typing import Literal

from sqlalchemy.orm import Session

from backend.app.db.models import Persona, Registro
from backend.app.services.event_service import register_entrada
from backend.app.ml.face_model import (
    get_embedding_from_bytes,
    bytes_to_embedding,
    embedding_to_bytes,
    find_best_match,
)
from backend.app.config.config import FACE_SIMILARITY_THRESHOLD


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
        # Obtener el embedding para guardarlo con el registro
        embedding = get_embedding_from_bytes(image_bytes)
        embedding_bytes = embedding_to_bytes(embedding) if embedding is not None else None
        register_entrada(
            db, 
            id_persona=result.person_id, 
            similarity_score=result.similarity,
            embedding_facial=embedding_bytes
        )
    return result


def _identify_person(db: Session, image_bytes: bytes) -> ValidateAccessResult:
    """Identifica persona por imagen (sin registrar evento). Usado por validate_access y register-exit."""
    embedding = get_embedding_from_bytes(image_bytes)
    if embedding is None:
        return ValidateAccessResult(allowed=False, reason="rostro_no_detectado")

    # Obtener embeddings de registro de personas activas
    rows = (
        db.query(Registro)
        .join(Persona, Registro.id_persona == Persona.id_persona)
        .filter(Persona.activo.is_(True), Registro.evento == "registro")
        .all()
    )
    
    if not rows:
        return ValidateAccessResult(allowed=False, reason="sin_personas_registradas")
    
    candidates = [(r.id_persona, bytes_to_embedding(r.embedding_facial)) for r in rows]
    match = find_best_match(embedding, candidates, threshold=FACE_SIMILARITY_THRESHOLD)

    if match is None:
        return ValidateAccessResult(allowed=False, reason="persona_no_identificada")

    person_id, sim = match
    
    return ValidateAccessResult(
        allowed=True,
        person_id=person_id,
        similarity=round(sim, 4),
        reason="acceso_permitido",
    )


