"""
Conexión y sesión SQLite. Referencia: docs/05-modelo-datos.md.
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from backend.app.core.config import DATABASE_URL

# SQLite: check_same_thread=False para uso con FastAPI (múltiples requests)
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia FastAPI: sesión por request; cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Crea todas las tablas en la BD (para script init_db)."""
    from backend.app.db import models  # noqa: F401 - registra modelos
    Base.metadata.create_all(bind=engine)


def ensure_registro_acceso_schema():
    """
    En SQLite, si la tabla registro_acceso tiene id_registro como BIGINT
    no se autoincrementa y falla NOT NULL. Recrea la tabla con INTEGER.
    Se llama al arranque de la app para auto-corregir BDs antiguas.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return
    from backend.app.db import models  # noqa: F401
    from backend.app.db.models import RegistroAcceso
    needs_fix = False
    with engine.connect() as conn:
        try:
            r = conn.execute(
                text("SELECT type FROM pragma_table_info('registro_acceso') WHERE name='id_registro'")
            )
            row = r.fetchone()
            if row:
                col_type = (row[0] or "").upper()
                needs_fix = "BIGINT" in col_type
        except Exception:
            pass  # Tabla no existe, create_all se encargará
    if needs_fix:
        RegistroAcceso.__table__.drop(engine, checkfirst=True)
        RegistroAcceso.__table__.create(engine)


def ensure_persona_visitante_columns():
    """
    Añade columnas HU-03 (motivo_visita, id_empleado_visitado) a persona si no existen.
    """
    if not DATABASE_URL.startswith("sqlite"):
        return
    with engine.connect() as conn:
        r = conn.execute(text("SELECT name FROM pragma_table_info('persona')"))
        names = {row[0] for row in r.fetchall()}
        if "motivo_visita" not in names:
            conn.execute(text("ALTER TABLE persona ADD COLUMN motivo_visita VARCHAR(500)"))
        if "id_empleado_visitado" not in names:
            conn.execute(text("ALTER TABLE persona ADD COLUMN id_empleado_visitado INTEGER"))
        conn.commit()


def ensure_autorizacion_table():
    """Crea la tabla autorizacion (HU-04) si no existe."""
    if not DATABASE_URL.startswith("sqlite"):
        return
    from backend.app.db import models  # noqa: F401
    from backend.app.db.models import Autorizacion
    with engine.connect() as conn:
        r = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' AND name='autorizacion'"))
        if r.fetchone() is None:
            Autorizacion.__table__.create(engine)
