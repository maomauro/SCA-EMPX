"""
Endpoints de consulta del historial de eventos de acceso.

Permite al dashboard listar y contar los eventos de entrada/salida
registrados por el pipeline de reconocimiento facial.

Rutas:
    GET /events/      → Lista paginada de eventos con filtro por tipo.
    GET /events/hoy   → Conteo de accesos del día actual (hora Colombia).
"""
from datetime import datetime, timezone, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Registro, Persona

# Zona horaria Colombia UTC-5
COL_TZ = timezone(timedelta(hours=-5))

router = APIRouter()


@router.get("/")
def listar_eventos(
    tipo:   Optional[str] = Query(None, description="'entrada' | 'salida'"),
    limit:  int           = Query(100, ge=1, le=500),
    offset: int           = Query(0,   ge=0),
    db: Session = Depends(get_db),
):
    """Lista eventos de acceso con paginación y filtro opcional por tipo.

    Args:
        tipo:   Filtra por ``'entrada'`` o ``'salida'``. ``None`` retorna ambos.
        limit:  Máximo de resultados (1–500, default 100).
        offset: Desplazamiento para paginación (default 0).
        db:     Sesión de base de datos.

    Returns:
        Lista de dicts con ``id_registro``, ``id_persona``, ``nombres``,
        ``tipo_acceso``, ``similitud`` y ``fecha``, ordenados del más
        reciente al más antiguo.
    """
    q = (
        db.query(Registro)
        .join(Persona, Registro.id_persona == Persona.id_persona)
        .filter(Registro.evento == "acceso")
    )

    if tipo in ("entrada", "salida"):
        q = q.filter(Registro.tipo_acceso == tipo)

    registros = q.order_by(Registro.fecha.desc()).offset(offset).limit(limit).all()

    return [
        {
            "id_registro": r.id_registro,
            "id_persona":  r.id_persona,
            "nombres":     r.persona.nombres if r.persona else "—",
            "tipo_acceso": r.tipo_acceso,
            "similitud":   r.similitud,
            "fecha":       r.fecha,
        }
        for r in registros
    ]


@router.get("/hoy")
def accesos_hoy(db: Session = Depends(get_db)):
    """Retorna el conteo de accesos registrados en el día actual.

    Usa la zona horaria de Colombia (UTC-5) para delimitar el día.
    La BD almacena fechas en UTC, por lo que el rango se convierte antes
    de consultar.

    Args:
        db: Sesión de base de datos.

    Returns:
        Dict ``{"fecha": "YYYY-MM-DD", "total": <int>}`` con el conteo
        de eventos de acceso del día actual.
    """
    ahora_col   = datetime.now(COL_TZ)
    inicio_col  = ahora_col.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_col     = inicio_col + timedelta(days=1)

    # Convertir a UTC naive para comparar con la BD
    inicio_utc = inicio_col.astimezone(timezone.utc).replace(tzinfo=None)
    fin_utc    = fin_col.astimezone(timezone.utc).replace(tzinfo=None)

    total = (
        db.query(Registro)
        .filter(
            Registro.evento == "acceso",
            Registro.fecha >= inicio_utc,
            Registro.fecha <  fin_utc,
        )
        .count()
    )
    return {"fecha": ahora_col.date().isoformat(), "total": total}


@router.get("/estadisticas")
def estadisticas_accesos(db: Session = Depends(get_db)):
    """Retorna estadísticas generales de accesos.

    Returns:
        Dict con estadísticas: total_hoy, total_entradas_hoy, total_salidas_hoy,
        personas_dentro, total_personas_registradas.
    """
    ahora_col   = datetime.now(COL_TZ)
    inicio_col  = ahora_col.replace(hour=0, minute=0, second=0, microsecond=0)
    fin_col     = inicio_col + timedelta(days=1)

    inicio_utc = inicio_col.astimezone(timezone.utc).replace(tzinfo=None)
    fin_utc    = fin_col.astimezone(timezone.utc).replace(tzinfo=None)

    # Total de accesos hoy
    total_hoy = (
        db.query(Registro)
        .filter(
            Registro.evento == "acceso",
            Registro.fecha >= inicio_utc,
            Registro.fecha < fin_utc,
        )
        .count()
    )

    # Entradas hoy
    entradas_hoy = (
        db.query(Registro)
        .filter(
            Registro.evento == "acceso",
            Registro.tipo_acceso == "entrada",
            Registro.fecha >= inicio_utc,
            Registro.fecha < fin_utc,
        )
        .count()
    )

    # Salidas hoy
    salidas_hoy = (
        db.query(Registro)
        .filter(
            Registro.evento == "acceso",
            Registro.tipo_acceso == "salida",
            Registro.fecha >= inicio_utc,
            Registro.fecha < fin_utc,
        )
        .count()
    )

    # Personas dentro (entradas - salidas hoy)
    personas_dentro = max(0, entradas_hoy - salidas_hoy)

    # Total de personas registradas activas
    total_personas = db.query(Persona).filter(Persona.activo.is_(True)).count()

    return {
        "total_hoy": total_hoy,
        "entradas_hoy": entradas_hoy,
        "salidas_hoy": salidas_hoy,
        "personas_dentro": personas_dentro,
        "total_personas": total_personas,
    }


@router.get("/recientes")
def eventos_recientes(
    minutos: int = Query(10, ge=1, le=1440, description="Minutos hacia atrás"),
    limit: int = Query(30, ge=1, le=100, description="Máximo de resultados"),
    db: Session = Depends(get_db),
):
    """Retorna eventos de acceso recientes.

    Args:
        minutos: Ventana de tiempo en minutos hacia atrás (default 10).
        limit: Máximo de resultados (default 30).
        db: Sesión de base de datos.

    Returns:
        Lista de eventos recientes ordenados del más reciente al más antiguo.
    """
    ahora_utc = datetime.now(timezone.utc).replace(tzinfo=None)
    desde_utc = ahora_utc - timedelta(minutes=minutos)

    registros = (
        db.query(Registro)
        .join(Persona, Registro.id_persona == Persona.id_persona)
        .filter(
            Registro.evento == "acceso",
            Registro.fecha >= desde_utc,
        )
        .order_by(Registro.fecha.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id_registro": r.id_registro,
            "id_persona": r.id_persona,
            "nombres": r.persona.nombres if r.persona else "—",
            "tipo_acceso": r.tipo_acceso,
            "similitud": r.similitud,
            "fecha": r.fecha,
        }
        for r in registros
    ]
