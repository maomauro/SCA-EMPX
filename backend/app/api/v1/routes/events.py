"""Rutas eventos entrada/salida. HU-06, HU-07, HU-08, HU-11."""
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.db.database import get_db
from backend.app.db.models import RegistroAcceso, Persona
from backend.app.schemas.event import EventoListItem, DashboardEstadisticas

router = APIRouter()

DEFAULT_LIMIT = 50
MAX_LIMIT = 100


def _query_eventos(
    db: Session,
    tipo: str | None = None,
    persona_id: int | None = None,
    documento: str | None = None,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    resultado: str | None = None,
):
    """Construye query de eventos con filtros. HU-08."""
    q = (
        db.query(RegistroAcceso)
        .join(Persona, RegistroAcceso.id_persona == Persona.id_persona)
        .order_by(RegistroAcceso.fecha_hora.desc())
    )
    if tipo in ("ingreso", "entrada"):
        q = q.filter(RegistroAcceso.tipo_movimiento == "ingreso")
    elif tipo == "salida":
        q = q.filter(RegistroAcceso.tipo_movimiento == "salida")
    if persona_id is not None:
        q = q.filter(RegistroAcceso.id_persona == persona_id)
    if documento and documento.strip():
        q = q.filter(Persona.documento.ilike("%" + documento.strip() + "%"))
    if fecha_desde and fecha_desde.strip():
        try:
            dt = datetime.strptime(fecha_desde.strip()[:10], "%Y-%m-%d")
            q = q.filter(RegistroAcceso.fecha_hora >= dt)
        except ValueError:
            pass
    if fecha_hasta and fecha_hasta.strip():
        try:
            dt = datetime.strptime(fecha_hasta.strip()[:10], "%Y-%m-%d")
            fin_dia = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            q = q.filter(RegistroAcceso.fecha_hora <= fin_dia)
        except ValueError:
            pass
    if resultado and resultado.strip() in ("permitido", "denegado"):
        q = q.filter(RegistroAcceso.resultado == resultado.strip())
    return q


@router.get("/", response_model=list[EventoListItem])
def listar_eventos(
    tipo: str | None = Query(None, description="ingreso | salida"),
    persona_id: int | None = Query(None, description="Filtrar por id_persona"),
    documento: str | None = Query(None, description="Filtrar por documento (parcial)"),
    fecha_desde: str | None = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: str | None = Query(None, description="YYYY-MM-DD"),
    resultado: str | None = Query(None, description="permitido | denegado"),
    limit: int = Query(DEFAULT_LIMIT, ge=1, le=MAX_LIMIT),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Lista eventos de acceso (registro_acceso). HU-06, HU-08.
    Filtros: tipo, persona_id, documento, fecha_desde, fecha_hasta, resultado. Paginación limit/offset (máx 100).
    """
    q = _query_eventos(db, tipo=tipo, persona_id=persona_id, documento=documento, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, resultado=resultado)
    rows = q.offset(offset).limit(limit).all()
    return [
        EventoListItem(
            id_registro=r.id_registro,
            id_persona=r.id_persona,
            nombre_completo=r.persona.nombre_completo if r.persona else None,
            tipo_movimiento=r.tipo_movimiento,
            fecha_hora=r.fecha_hora,
            resultado=r.resultado,
            similarity_score=r.similarity_score,
            metodo_identificacion=r.metodo_identificacion,
        )
        for r in rows
    ]


@router.get("/recientes", response_model=list[EventoListItem])
def listar_eventos_recientes(
    minutos: int = Query(10, ge=1, le=120, description="Últimos N minutos"),
    limit: int = Query(50, ge=1, le=MAX_LIMIT),
    db: Session = Depends(get_db),
):
    """
    Lista eventos de los últimos N minutos. HU-11 (dashboard).
    """
    desde = datetime.utcnow() - timedelta(minutes=minutos)
    rows = (
        db.query(RegistroAcceso)
        .join(Persona, RegistroAcceso.id_persona == Persona.id_persona)
        .filter(RegistroAcceso.fecha_hora >= desde)
        .order_by(RegistroAcceso.fecha_hora.desc())
        .limit(limit)
        .all()
    )
    return [
        EventoListItem(
            id_registro=r.id_registro,
            id_persona=r.id_persona,
            nombre_completo=r.persona.nombre_completo if r.persona else None,
            tipo_movimiento=r.tipo_movimiento,
            fecha_hora=r.fecha_hora,
            resultado=r.resultado,
            similarity_score=r.similarity_score,
            metodo_identificacion=r.metodo_identificacion,
        )
        for r in rows
    ]


@router.get("/estadisticas", response_model=DashboardEstadisticas)
def obtener_estadisticas_dashboard(db: Session = Depends(get_db)):
    """
    Métricas para dashboard: total personas dentro, accesos permitidos hoy, denegaciones hoy. HU-11.
    """
    hoy_inicio = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    accesos_hoy = (
        db.query(func.count(RegistroAcceso.id_registro))
        .filter(RegistroAcceso.fecha_hora >= hoy_inicio, RegistroAcceso.resultado == "permitido")
        .scalar()
        or 0
    )
    denegaciones_hoy = (
        db.query(func.count(RegistroAcceso.id_registro))
        .filter(RegistroAcceso.fecha_hora >= hoy_inicio, RegistroAcceso.resultado == "denegado")
        .scalar()
        or 0
    )
    # Personas cuyo último evento es ingreso permitido (están "dentro")
    subq = (
        db.query(RegistroAcceso.id_persona, func.max(RegistroAcceso.fecha_hora).label("max_fecha"))
        .group_by(RegistroAcceso.id_persona)
        .subquery()
    )
    total_dentro = (
        db.query(func.count(RegistroAcceso.id_registro))
        .join(subq, (RegistroAcceso.id_persona == subq.c.id_persona) & (RegistroAcceso.fecha_hora == subq.c.max_fecha))
        .filter(RegistroAcceso.tipo_movimiento == "ingreso", RegistroAcceso.resultado == "permitido")
        .scalar()
        or 0
    )
    return DashboardEstadisticas(total_dentro=total_dentro, accesos_hoy=accesos_hoy, denegaciones_hoy=denegaciones_hoy)


@router.get("/export", response_class=PlainTextResponse)
def exportar_eventos_csv(
    tipo: str | None = Query(None),
    persona_id: int | None = Query(None),
    documento: str | None = Query(None),
    fecha_desde: str | None = Query(None),
    fecha_hasta: str | None = Query(None),
    resultado: str | None = Query(None),
    limit: int = Query(MAX_LIMIT, ge=1, le=5000),
    db: Session = Depends(get_db),
):
    """
    Exporta eventos a CSV con los mismos filtros que GET /. HU-08. Máximo 5000 filas.
    """
    q = _query_eventos(db, tipo=tipo, persona_id=persona_id, documento=documento, fecha_desde=fecha_desde, fecha_hasta=fecha_hasta, resultado=resultado)
    rows = q.limit(limit).all()
    lines = ["id_registro;id_persona;nombre_completo;tipo_movimiento;fecha_hora;resultado;similarity_score;metodo_identificacion"]
    for r in rows:
        nombre = (r.persona.nombre_completo if r.persona else "") or ""
        nombre = nombre.replace(";", ",")
        lines.append(
            f"{r.id_registro};{r.id_persona};{nombre};{r.tipo_movimiento};{r.fecha_hora.isoformat() if r.fecha_hora else ''};{r.resultado};{r.similarity_score or ''};{r.metodo_identificacion}"
        )
    return "\n".join(lines)
