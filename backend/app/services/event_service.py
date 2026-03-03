"""
Servicio de registro de eventos de acceso (entrada/salida). HU-06, HU-07.
"""
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.db.models import Registro


def register_entrada(
    db: Session,
    id_persona: int,
    similarity_score: float,
    embedding_facial: bytes = None,
) -> Registro:
    """
    Registra un evento de entrada (ingreso) en registros. HU-06.
    Se invoca desde POST validate-access cuando el acceso es permitido.
    """
    reg = Registro(
        id_persona=id_persona,
        evento="acceso",
        tipo_acceso="entrada",
        embedding_facial=embedding_facial,
        similitud=similarity_score,
        fecha=datetime.now(timezone.utc),
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def register_salida(
    db: Session,
    id_persona: int,
    similarity_score: float | None = None,
    embedding_facial: bytes = None,
) -> Registro:
    """
    Registra un evento de salida en registros. HU-07.
    Se invoca desde POST register-exit cuando la persona es identificada por reconocimiento facial.
    """
    reg = Registro(
        id_persona=id_persona,
        evento="acceso",
        tipo_acceso="salida",
        embedding_facial=embedding_facial,
        similitud=similarity_score,
        fecha=datetime.now(timezone.utc),
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg
