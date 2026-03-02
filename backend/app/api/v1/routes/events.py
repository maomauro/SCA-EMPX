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
