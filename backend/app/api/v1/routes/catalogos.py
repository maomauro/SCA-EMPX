"""
Endpoints de catálogos — datos de referencia del sistema.

Expone los catálogos estáticos necesarios para poblar los formularios
del frontend: áreas organizacionales, cargos y tipos de persona.
Estos datos son de solo lectura desde la API; se modifican únicamente
a través del seed inicial o de migraciones.

Rutas:
    GET /catalogos/areas                  → Lista todas las áreas.
    GET /catalogos/areas/{id}/cargos      → Lista los cargos de un área.
    GET /catalogos/cargos                 → Lista todos los cargos.
    GET /catalogos/tipos-persona          → Lista los tipos de persona.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import Area, Cargo, TipoPersona

router = APIRouter()


@router.get("/areas")
def listar_areas(db: Session = Depends(get_db)):
    """Retorna todas las áreas organizacionales ordenadas alfabéticamente.

    Args:
        db: Sesión de base de datos.

    Returns:
        Lista de dicts ``{id_area, nombre}``.
    """
    areas = db.query(Area).order_by(Area.nombre).all()
    return [{"id_area": a.id_area, "nombre": a.nombre} for a in areas]


@router.get("/areas/{id_area}/cargos")
def listar_cargos_por_area(id_area: int, db: Session = Depends(get_db)):
    """Retorna los cargos pertenecientes a un área específica.

    Args:
        id_area: Identificador del área.
        db:      Sesión de base de datos.

    Returns:
        Lista de dicts ``{id_cargo, nombre, id_area}`` ordenada por nombre.
    """
    cargos = db.query(Cargo).filter(Cargo.id_area == id_area).order_by(Cargo.nombre).all()
    return [{"id_cargo": c.id_cargo, "nombre": c.nombre, "id_area": c.id_area} for c in cargos]


@router.get("/cargos")
def listar_cargos(db: Session = Depends(get_db)):
    """Retorna todos los cargos del sistema sin filtro de área.

    Args:
        db: Sesión de base de datos.

    Returns:
        Lista de dicts ``{id_cargo, nombre, id_area}`` ordenada por nombre.
    """
    cargos = db.query(Cargo).order_by(Cargo.nombre).all()
    return [{"id_cargo": c.id_cargo, "nombre": c.nombre, "id_area": c.id_area} for c in cargos]


@router.get("/tipos-persona")
def listar_tipos(db: Session = Depends(get_db)):
    """Retorna todos los tipos de persona registrados en el sistema.

    Args:
        db: Sesión de base de datos.

    Returns:
        Lista de dicts ``{id_tipo_persona, tipo, es_empleado}`` ordenada
        alfabéticamente.
    """
    tipos = db.query(TipoPersona).order_by(TipoPersona.tipo).all()
    return [{"id_tipo_persona": t.id_tipo_persona, "tipo": t.tipo, "es_empleado": t.es_empleado} for t in tipos]
