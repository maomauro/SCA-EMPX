"""
Conexión y sesión SQLite. Referencia: docs/05-modelo-datos.md.
"""
from sqlalchemy import create_engine
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
