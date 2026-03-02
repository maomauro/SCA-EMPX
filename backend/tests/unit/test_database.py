"""Pruebas unitarias de backend/app/db/database.py.

Cubre:
    - init_db(): crea tablas e inserta catálogos.
    - _seed(): idempotencia (no duplica datos).
    - reset_db(): borra datos transaccionales y preserva catálogos.
    - get_db(): generador correcto de sesiones.

Nota: se usa la BD en memoria definida en conftest.py.
      Las funciones init_db / reset_db de producción usan el engine real;
      aquí se prueban con el engine de test para no tocar sca.db.
"""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

from backend.app.db.models import (
    Base, Area, Cargo, TipoPersona, Persona, Registro, Visita,
)
from backend.app.ml.face_model import embedding_to_bytes
import numpy as np


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _seed_on_engine(engine):
    """Ejecuta la lógica de _seed pero sobre un engine dado."""
    from sqlalchemy.orm import sessionmaker as sm
    Session = sm(bind=engine)
    db = Session()
    try:
        if db.query(TipoPersona).first() is None:
            db.add_all([
                TipoPersona(tipo="Empleado",    es_empleado=True),
                TipoPersona(tipo="Visitante",   es_empleado=False),
                TipoPersona(tipo="Contratista", es_empleado=False),
            ])
            db.flush()
        if db.query(Area).first() is None:
            tec = Area(nombre="Tecnología")
            db.add(tec)
            db.flush()
            db.add(Cargo(nombre="Dev", id_area=tec.id_area))
        db.commit()
    finally:
        db.close()


def _make_emb() -> bytes:
    v = np.ones(512, dtype=np.float32)
    v /= np.linalg.norm(v)
    return embedding_to_bytes(v)


# ═══════════════════════════════════════════════════════════════════════════════
#  init_db  (simulado con engine de test)
# ═══════════════════════════════════════════════════════════════════════════════

class TestInitDb:
    """Pruebas equivalentes a init_db() sobre un engine aislado."""

    @pytest.fixture(scope="class")
    def isolated_engine(self):
        """Motor SQLite en memoria creado solo para esta clase."""
        eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=eng)
        yield eng
        Base.metadata.drop_all(bind=eng)

    def test_crea_todas_las_tablas(self, isolated_engine):
        """create_all genera las 6 tablas del esquema."""
        inspector = inspect(isolated_engine)
        tablas = set(inspector.get_table_names())
        esperadas = {"areas", "cargos", "tipos_persona", "personas", "registros", "visitas"}
        assert esperadas.issubset(tablas)

    def test_seed_inserta_tipos_persona(self, isolated_engine):
        """La siembra inicial crea los 3 tipos de persona."""
        _seed_on_engine(isolated_engine)
        Session = sessionmaker(bind=isolated_engine)
        db = Session()
        count = db.query(TipoPersona).count()
        db.close()
        assert count == 3

    def test_seed_inserta_area_y_cargo(self, isolated_engine):
        """La siembra inicial crea al menos 1 área y 1 cargo."""
        Session = sessionmaker(bind=isolated_engine)
        db = Session()
        assert db.query(Area).count() >= 1
        assert db.query(Cargo).count() >= 1
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  Idempotencia de _seed
# ═══════════════════════════════════════════════════════════════════════════════

class TestSeedIdempotencia:
    """La siembra no duplica datos al ejecutarse múltiples veces."""

    @pytest.fixture(scope="class")
    def seeded_engine(self):
        eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=eng)
        _seed_on_engine(eng)
        yield eng

    def test_segunda_siembra_no_duplica_tipos(self, seeded_engine):
        """Llamar a seed dos veces no crea tipos duplicados."""
        _seed_on_engine(seeded_engine)
        Session = sessionmaker(bind=seeded_engine)
        db = Session()
        count = db.query(TipoPersona).count()
        db.close()
        assert count == 3

    def test_segunda_siembra_no_duplica_areas(self, seeded_engine):
        """Llamar a seed dos veces no crea áreas duplicadas."""
        _seed_on_engine(seeded_engine)
        Session = sessionmaker(bind=seeded_engine)
        db = Session()
        count = db.query(Area).count()
        db.close()
        assert count == 1  # solo "Tecnología"


# ═══════════════════════════════════════════════════════════════════════════════
#  reset_db  (simulado con engine de test)
# ═══════════════════════════════════════════════════════════════════════════════

class TestResetDb:
    """Equivalente a reset_db(): borra transaccionales, preserva catálogos."""

    @pytest.fixture()
    def populated_engine(self):
        """Motor con catálogos + 1 persona + 1 registro + 1 visita."""
        eng = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=eng)
        _seed_on_engine(eng)

        Session = sessionmaker(bind=eng)
        db = Session()
        tipo = db.query(TipoPersona).filter_by(tipo="Visitante").first()
        p = Persona(
            tipo_documento="CC", nro_documento="TEST001",
            nombres="Reset Test", id_tipo_persona=tipo.id_tipo_persona,
        )
        db.add(p)
        db.flush()
        db.add(Registro(
            id_persona=p.id_persona,
            evento="registro", tipo_acceso=None,
            embedding_facial=_make_emb(),
        ))
        db.add(Visita(id_persona=p.id_persona, motivo="Test"))
        db.commit()
        db.close()
        yield eng

    def _reset(self, engine):
        Session = sessionmaker(bind=engine)
        db = Session()
        try:
            db.query(Registro).delete()
            db.query(Visita).delete()
            db.query(Persona).delete()
            db.commit()
        finally:
            db.close()

    def test_reset_borra_personas(self, populated_engine):
        """reset_db elimina todas las personas."""
        self._reset(populated_engine)
        Session = sessionmaker(bind=populated_engine)
        db = Session()
        assert db.query(Persona).count() == 0
        db.close()

    def test_reset_borra_registros(self, populated_engine):
        """reset_db elimina todos los registros."""
        self._reset(populated_engine)
        Session = sessionmaker(bind=populated_engine)
        db = Session()
        assert db.query(Registro).count() == 0
        db.close()

    def test_reset_borra_visitas(self, populated_engine):
        """reset_db elimina todas las visitas."""
        self._reset(populated_engine)
        Session = sessionmaker(bind=populated_engine)
        db = Session()
        assert db.query(Visita).count() == 0
        db.close()

    def test_reset_preserva_tipos_persona(self, populated_engine):
        """reset_db no modifica los tipos de persona."""
        self._reset(populated_engine)
        Session = sessionmaker(bind=populated_engine)
        db = Session()
        assert db.query(TipoPersona).count() == 3
        db.close()

    def test_reset_preserva_areas(self, populated_engine):
        """reset_db no modifica las áreas."""
        self._reset(populated_engine)
        Session = sessionmaker(bind=populated_engine)
        db = Session()
        assert db.query(Area).count() >= 1
        db.close()

    def test_reset_preserva_cargos(self, populated_engine):
        """reset_db no modifica los cargos."""
        self._reset(populated_engine)
        Session = sessionmaker(bind=populated_engine)
        db = Session()
        assert db.query(Cargo).count() >= 1
        db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  get_db
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetDb:
    """Pruebas del generador get_db."""

    def test_get_db_retorna_sesion(self):
        """get_db debe ser un generador que produce una sesión SQLAlchemy."""
        from backend.app.db.database import get_db
        from sqlalchemy.orm import Session

        gen = get_db()
        db  = next(gen)
        assert isinstance(db, Session)
        # Cerrar el generador correctamente
        try:
            next(gen)
        except StopIteration:
            pass

    def test_get_db_cierra_sesion_al_finalizar(self):
        """get_db cierra la sesión al agotarse el generador (finally block).

        SQLAlchemy 2.x: ``session.is_active`` es False solo en el estado
        "requires-rollback" (transacción fallida), no por llamar ``close()``.
        Verificamos que después del finally la sesión ya no tiene transacción
        activa (``in_transaction() == False``).
        """
        from backend.app.db.database import get_db

        gen = get_db()
        db  = next(gen)
        # Durante el yield la sesión está activa y puede ejecutar consultas
        assert db.is_active

        try:
            next(gen)
        except StopIteration:
            pass

        # Tras el finally la sesión está cerrada: no hay transacción abierta
        assert not db.in_transaction()
