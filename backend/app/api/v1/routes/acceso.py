"""
Endpoint de validación de acceso facial — núcleo del sistema.

Expone un único endpoint ``POST /acceso/validar`` que recibe un frame de
cámara, identifica al individuo comparando su embedding con la galería
almacenada y registra el evento de entrada o salida.

Características:
    - **Aprendizaje progresivo**: si la similitud supera
      ``FACE_HIGH_CONFIDENCE_THRESHOLD``, el embedding se incorpora
      automáticamente a la galería (hasta ``MAX_EMBEDDINGS_PER_PERSONA``).
    - **Alternancia automática**: determina entrada/salida basándose en el
      historial del día con protección anti-rebote (``ACCESO_TOGGLE_MINUTOS``).
    - **Tiempo real**: emite el resultado por WebSocket tras cada evento.
    - **Cierre de visita**: si el individuo es visitante/contratista y sale,
      registra automáticamente la hora de salida en la tabla ``visitas``.
"""
import asyncio
import logging
from datetime import datetime, date, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Persona, Registro, Visita
from backend.app.ml.face_model import (
    get_embedding_from_bytes, embedding_to_bytes, bytes_to_embedding,
    find_best_match,
)
from backend.app.config.config import (
    FACE_SIMILARITY_THRESHOLD,
    FACE_HIGH_CONFIDENCE_THRESHOLD,
    MAX_EMBEDDINGS_PER_PERSONA,
)
from backend.app.api.v1.routes.ws import manager

log = logging.getLogger("sca.acceso")
router = APIRouter()

# ── Umbral de alternancia entrada/salida ─────────────────────────────────────
# Tiempo mínimo entre dos detecciones para considerar que es un nuevo evento.
# < umbral  → idempotente (mantiene el tipo anterior)
# >= umbral → alterna al tipo contrario
# NOTA: cambiar a 10 para producción
ACCESO_TOGGLE_MINUTOS: int = 1


def _determinar_tipo_acceso(db: Session, id_persona: int) -> str:
    """Determina si el siguiente evento de la persona es entrada o salida.

    Aplica tres reglas en orden sobre el historial de accesos del día actual
    (el contador se reinicia a las 00:00 hora local):

    1. Sin registros hoy → ``'entrada'``.
    2. Último evento hace menos de ``ACCESO_TOGGLE_MINUTOS`` → mismo tipo
       (idempotente, evita rebotes por frames duplicados).
    3. Último evento hace más del umbral → alterna ``'entrada'`` ⊕ ``'salida'``.

    Args:
        db:         Sesión activa de SQLAlchemy.
        id_persona: Identificador de la persona a evaluar.

    Returns:
        ``'entrada'`` o ``'salida'`` según las reglas anteriores.
    """
    inicio_hoy = datetime.combine(date.today(), datetime.min.time())

    ultimo = (
        db.query(Registro)
        .filter(
            Registro.id_persona == id_persona,
            Registro.evento     == "acceso",
            Registro.fecha      >= inicio_hoy,
        )
        .order_by(Registro.fecha.desc())
        .first()
    )

    if ultimo is None:
        return "entrada"

    delta  = datetime.now(timezone.utc) - ultimo.fecha.replace(tzinfo=timezone.utc)
    umbral = timedelta(minutes=ACCESO_TOGGLE_MINUTOS)

    if delta < umbral:
        return ultimo.tipo_acceso          # idempotente: sin rebote
    return "salida" if ultimo.tipo_acceso == "entrada" else "entrada"


def _get_candidatos(db: Session) -> list[tuple[int, any]]:
    """Carga la galería de embeddings de referencia desde la base de datos.

    Solo recupera registros de personas activas con ``evento='registro'``.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        Lista de tuplas ``(id_persona, embedding_array)`` lista para pasar
        a ``find_best_match``.
    """
    rows = (
        db.query(Registro)
        .join(Persona, Registro.id_persona == Persona.id_persona)
        .filter(Persona.activo, Registro.evento == "registro")
        .all()
    )
    return [(r.id_persona, bytes_to_embedding(r.embedding_facial)) for r in rows]


@router.post("/validar")
def validar_acceso(
    foto: UploadFile = File(..., description="Frame de cámara (JPEG/PNG)"),
    db: Session = Depends(get_db),
):
    """Valida el acceso facial y registra el evento de entrada o salida.

    Flujo:
        1. Decodifica la imagen y extrae el embedding facial.
        2. Compara el embedding contra la galería de referencia en BD.
        3. Registra el evento de acceso y aplica aprendizaje progresivo
           si la similitud supera ``FACE_HIGH_CONFIDENCE_THRESHOLD``.
        4. Cierra la visita activa si el individuo es no-empleado saliente.
        5. Emite el evento por WebSocket (fire-and-forget).

    Args:
        foto: Imagen del frame capturado por la cámara (JPEG o PNG).
        db:   Sesión de base de datos inyectada por FastAPI.

    Returns:
        Dict con ``permitido``, ``tipo_acceso``, ``similitud`` y ``persona``
        si el acceso fue concedido, o ``permitido=False`` con ``motivo``
        si no se identificó al individuo.

    Raises:
        HTTPException: 400 si la imagen está vacía.
    """
    img_bytes = foto.file.read()
    if not img_bytes:
        raise HTTPException(400, "Imagen vacía.")

    # 1. Embedding
    emb = get_embedding_from_bytes(img_bytes)
    if emb is None:
        return {
            "permitido": False,
            "motivo": "rostro_no_detectado",
            "persona": None,
            "similitud": None,
        }

    # 2. Comparar
    candidatos = _get_candidatos(db)
    if not candidatos:
        return {
            "permitido": False,
            "motivo": "sin_personas_registradas",
            "persona": None,
            "similitud": None,
        }

    match = find_best_match(emb, candidatos, threshold=FACE_SIMILARITY_THRESHOLD)

    if match is None:
        log.info("Acceso denegado — sin match (candidatos: %s)", len(candidatos))
        return {
            "permitido": False,
            "motivo": "persona_no_identificada",
            "persona": None,
            "similitud": None,
        }

    id_persona, similitud = match
    tipo_acceso = _determinar_tipo_acceso(db, id_persona)

    # 3. Registrar evento de acceso
    reg_acceso = Registro(
        id_persona=id_persona,
        evento="acceso",
        tipo_acceso=tipo_acceso,
        embedding_facial=embedding_to_bytes(emb),
        similitud=similitud,
    )
    db.add(reg_acceso)

    # 3b. Aprendizaje progresivo — solo si alta confianza y no supera el límite
    if similitud >= FACE_HIGH_CONFIDENCE_THRESHOLD:
        n_refs = db.query(Registro).filter(
            Registro.id_persona == id_persona,
            Registro.evento == "registro",
        ).count()
        if n_refs < MAX_EMBEDDINGS_PER_PERSONA:
            nuevo_ref = Registro(
                id_persona=id_persona,
                evento="registro",
                tipo_acceso=None,
                embedding_facial=embedding_to_bytes(emb),
                similitud=similitud,
            )
            db.add(nuevo_ref)
            log.info("Aprendizaje progresivo: nuevo embedding para persona %s (sim=%s)", id_persona, similitud)

    db.commit()

    # Obtener datos de la persona para la respuesta
    persona = db.query(Persona).filter(Persona.id_persona == id_persona).first()
    es_empleado = persona.tipo_persona.es_empleado if persona.tipo_persona else True

    # Si es visitante/contratista saliendo → cerrar visita activa
    visita_cerrada = False
    if not es_empleado and tipo_acceso == "salida":
        visita_activa = (
            db.query(Visita)
            .filter(
                Visita.id_persona    == id_persona,
                Visita.fecha_salida  == None,  # noqa: E711
            )
            .order_by(Visita.fecha.desc())
            .first()
        )
        if visita_activa:
            visita_activa.fecha_salida = datetime.now(timezone.utc)
            db.commit()
            visita_cerrada = True
            log.info("Visita %s cerrada por salida facial de %s", visita_activa.id_visita, persona.nombres)

    persona_data = {
        "id_persona":          persona.id_persona,
        "nombres":             persona.nombres,
        "tipo":                persona.tipo_persona.tipo if persona.tipo_persona else "",
        "es_empleado":         es_empleado,
        "visitante_de_salida": visita_cerrada,
    }

    # 4. Broadcast WebSocket (fire-and-forget)
    payload = {
        "type": "acceso",
        "data": {
            "id_persona":   id_persona,
            "nombres":      persona.nombres,
            "tipo_acceso":  tipo_acceso,
            "similitud":    similitud,
            "fecha":        datetime.now(timezone.utc).isoformat(),
        },
    }
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(manager.broadcast(payload))
    except Exception:
        pass

    log.info("Acceso %s: %s (sim=%s)", tipo_acceso, persona.nombres, similitud)

    return {
        "permitido":   True,
        "tipo_acceso": tipo_acceso,
        "similitud":   similitud,
        "persona":     persona_data,
    }
