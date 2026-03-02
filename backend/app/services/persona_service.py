"""
Servicio de registro de personas (empleados y visitantes). HU-01, HU-03.
"""
from sqlalchemy.orm import Session

from backend.app.db.models import Persona, ReconocimientoFacial, TipoPersona
from backend.app.ml.inference import get_embedding_from_image, embedding_to_bytes, MODEL_NAME


def get_tipo_persona_id(db: Session, nombre_tipo: str) -> int | None:
    """Obtiene id_tipo_persona por nombre (ej. empleado_propio, visitante_temporal)."""
    row = db.query(TipoPersona).filter(TipoPersona.nombre_tipo == nombre_tipo).first()
    return row.id_tipo_persona if row else None


def documento_existe(db: Session, documento: str) -> bool:
    return db.query(Persona).filter(Persona.documento == documento).first() is not None


def registrar_empleado(
    db: Session,
    nombre_completo: str,
    documento: str,
    cargo: str | None = None,
    area: str | None = None,
    tipo_documento: str = "CC",
    image_bytes: bytes | None = None,
) -> tuple[Persona, ReconocimientoFacial | None, float | None]:
    """
    Registra un empleado con foto. Genera embedding y persiste persona + reconocimiento_facial.
    Retorna (persona, reconocimiento_facial, calidad_embedding o None).
    Lanza ValueError si documento duplicado o si no se detecta un rostro en la foto.
    """
    if documento_existe(db, documento):
        raise ValueError("documento_duplicado")

    id_tipo = get_tipo_persona_id(db, "empleado_propio")
    if not id_tipo:
        raise ValueError("tipo_persona_no_configurado")

    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("foto_requerida")

    embedding = get_embedding_from_image(image_bytes)
    if embedding is None:
        raise ValueError("rostro_no_detectado")

    persona = Persona(
        id_tipo_persona=id_tipo,
        nombre_completo=nombre_completo.strip(),
        documento=documento.strip(),
        tipo_documento=tipo_documento.strip() or "CC",
        cargo=(cargo or "").strip() or None,
        area=(area or "").strip() or None,
        estado="activo",
    )
    db.add(persona)
    db.flush()  # para obtener persona.id_persona

    embedding_bytes = embedding_to_bytes(embedding)
    # Calidad opcional: DeepFace no devuelve score directo, se puede dejar None
    calidad = None
    reco = ReconocimientoFacial(
        id_persona=persona.id_persona,
        embedding=embedding_bytes,
        modelo_version=MODEL_NAME,
        estado="activo",
        calidad_embedding=calidad,
    )
    db.add(reco)
    db.commit()
    db.refresh(persona)
    db.refresh(reco)
    return persona, reco, calidad


def registrar_visitante(
    db: Session,
    nombre_completo: str,
    documento: str,
    empresa: str,
    motivo_visita: str,
    tipo_documento: str = "CC",
    id_empleado_visitado: int | None = None,
    image_bytes: bytes | None = None,
) -> tuple[Persona, ReconocimientoFacial | None, float | None]:
    """
    Registra un visitante con foto. Misma lógica que empleado: documento único, embedding Facenet.
    Retorna (persona, reconocimiento_facial, calidad_embedding o None).
    """
    if documento_existe(db, documento):
        raise ValueError("documento_duplicado")

    id_tipo = get_tipo_persona_id(db, "visitante_temporal")
    if not id_tipo:
        raise ValueError("tipo_persona_no_configurado")

    if not image_bytes or len(image_bytes) == 0:
        raise ValueError("foto_requerida")

    embedding = get_embedding_from_image(image_bytes)
    if embedding is None:
        raise ValueError("rostro_no_detectado")

    persona = Persona(
        id_tipo_persona=id_tipo,
        nombre_completo=nombre_completo.strip(),
        documento=documento.strip(),
        tipo_documento=tipo_documento.strip() or "CC",
        empresa=(empresa or "").strip() or None,
        motivo_visita=(motivo_visita or "").strip() or None,
        id_empleado_visitado=id_empleado_visitado,
        estado="activo",
    )
    db.add(persona)
    db.flush()

    embedding_bytes = embedding_to_bytes(embedding)
    reco = ReconocimientoFacial(
        id_persona=persona.id_persona,
        embedding=embedding_bytes,
        modelo_version=MODEL_NAME,
        estado="activo",
        calidad_embedding=None,
    )
    db.add(reco)
    db.commit()
    db.refresh(persona)
    db.refresh(reco)
    return persona, reco, None
