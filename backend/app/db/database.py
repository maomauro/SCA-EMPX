"""Configuración de la conexión a la base de datos, sesión SQLAlchemy y datos de fábrica.

Este módulo centraliza:
- La creación del motor SQLAlchemy apuntando a la URL definida en ``config``.
- La fábrica de sesiones ``SessionLocal`` usada por los endpoints vía ``get_db``.
- ``init_db``: crea las tablas si no existen y siembra los catálogos iniciales.
- ``reset_db``: limpia personas, registros y visitas dejando los catálogos intactos.
- ``_seed``: inserta los datos de fábrica de forma idempotente.

Uso típico en el arranque de la aplicación::

    from backend.app.db.database import init_db
    init_db()
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.config.config import DATABASE_URL
from backend.app.db.models import Base, Area, Cargo, TipoPersona, Persona, Registro, Visita  # noqa: F401


connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Generador de sesiones de base de datos para inyección de dependencias FastAPI.

    Abre una sesión, la cede al endpoint y garantiza su cierre al finalizar la
    solicitud, independientemente de si ocurrió una excepción.

    Yields:
        Session: Sesión SQLAlchemy lista para consultas y transacciones.

    Example::

        @router.get("/items")
        def list_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas del esquema y siembra los catálogos iniciales.

    Llama a ``Base.metadata.create_all`` (no destruye tablas existentes) y
    luego a ``_seed`` para insertar los datos de fábrica si las tablas están
    vacías. Es seguro ejecutarlo en cada arranque de la aplicación.
    """
    Base.metadata.create_all(bind=engine)
    _seed()


def reset_db():
    """Restablece la base de datos a su estado de fábrica.

    Elimina todos los registros de las tablas transaccionales en el orden
    correcto para respetar las restricciones de llave foránea:
    ``Registro`` → ``Visita`` → ``Persona``.

    Las tablas de catálogo (``areas``, ``cargos``, ``tipos_persona``) **no**
    se modifican.

    Note:
        Esta operación es irreversible. Úsala solo en entornos de desarrollo
        o cuando se requiera un reinicio total de los datos operativos.
    """
    db = SessionLocal()
    try:
        db.query(Registro).delete()
        db.query(Visita).delete()
        db.query(Persona).delete()
        db.commit()
    finally:
        db.close()


def _seed():
    """Inserta los catálogos de fábrica si las tablas correspondientes están vacías.

    Siembra en orden para satisfacer las dependencias de FK:

    1. **TipoPersona**: Empleado, Visitante, Contratista.
    2. **Area**: Tecnología, Recursos Humanos, Operaciones.
    3. **Cargo**: tres cargos por área (nueve en total).

    Cada bloque verifica si ya existe al menos un registro antes de insertar,
    por lo que es seguro llamar a esta función múltiples veces (idempotente).

    Note:
        Esta función es de uso interno; invócala a través de ``init_db``.
    """
    db = SessionLocal()
    try:
        # ── Tipos de persona ──────────────────────────────────────────────
        if db.query(TipoPersona).first() is None:
            tipos = [
                TipoPersona(
                    tipo="Empleado",
                    descripcion="Empleado directo de la empresa",
                    es_empleado=True),
                TipoPersona(
                    tipo="Visitante",
                    descripcion="Visitante externo",
                    es_empleado=False),
                TipoPersona(
                    tipo="Contratista",
                    descripcion="Personal de empresa contratista",
                    es_empleado=False),
            ]
            db.add_all(tipos)
            db.flush()

        # ── Áreas ─────────────────────────────────────────────────────────
        if db.query(Area).first() is None:
            areas_data = ["Tecnología", "Recursos Humanos", "Operaciones"]
            areas = [Area(nombre=n) for n in areas_data]
            db.add_all(areas)
            db.flush()

            # ── Cargos (3 por área) ───────────────────────────────────────
            cargos_por_area = {
                "Tecnología":[
                    "Desarrollador",
                    "Analista de Sistemas",
                    "Arquitecto de Software"],
                "Recursos Humanos": [
                    "Gestor de Talento",
                    "Coordinador RRHH",
                    "Analista de Nómina"],
                "Operaciones": [
                    "Supervisor",
                    "Operador de Planta",
                    "Técnico de Mantenimiento"],
            }
            area_map: dict[str, Area] = {str(a.nombre): a for a in areas}
            for area_nombre, cargos in cargos_por_area.items():
                area = area_map[area_nombre]
                for cargo_nombre in cargos:
                    db.add(Cargo(nombre=cargo_nombre, id_area=area.id_area))

        db.commit()
    finally:
        db.close()
