"""
Servicio de registro de eventos de acceso (entrada/salida). HU-06, HU-07.
"""
from sqlalchemy.orm import Session

from backend.app.db.models import RegistroAcceso


def register_entrada(
    db: Session,
    id_persona: int,
    similarity_score: float,
    metodo_identificacion: str = "reconocimiento_facial",
) -> RegistroAcceso:
    """
    Registra un evento de entrada (ingreso) en registro_acceso. HU-06.
    Se invoca desde POST validate-access cuando el acceso es permitido.
    """
    reg = RegistroAcceso(
        id_persona=id_persona,
        tipo_movimiento="ingreso",
        metodo_identificacion=metodo_identificacion,
        resultado="permitido",
        similarity_score=similarity_score,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def register_salida(
    db: Session,
    id_persona: int,
    similarity_score: float | None = None,
    metodo_identificacion: str = "reconocimiento_facial",
) -> RegistroAcceso:
    """
    Registra un evento de salida en registro_acceso. HU-07.
    Se invoca desde POST register-exit cuando la persona es identificada por reconocimiento facial.
    """
    reg = RegistroAcceso(
        id_persona=id_persona,
        tipo_movimiento="salida",
        metodo_identificacion=metodo_identificacion,
        resultado="permitido",
        similarity_score=similarity_score,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg
