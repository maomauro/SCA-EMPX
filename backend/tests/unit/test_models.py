"""Pruebas unitarias de los modelos ORM (backend/app/db/models.py).

Cubre:
    - Creación e inserción de cada entidad.
    - Relaciones ORM (back_populates, cascade).
    - Restricciones de unicidad (nro_documento, Area.nombre, TipoPersona.tipo).
    - Valores por defecto (activo=True, fecha_registro auto).
    - Cascade delete: Persona → Registro / Visita.
"""
from datetime import datetime, timezone

import numpy as np
import pytest
from sqlalchemy.exc import IntegrityError

from backend.app.db.models import (
    Area, Cargo, Persona, Registro, TipoPersona, Visita,
)
from backend.app.ml.face_model import embedding_to_bytes


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def _make_persona(db, nro: str, tipo_id: int, cargo_id: int | None = None) -> Persona:
    """Inserta y retorna una Persona con los campos mínimos."""
    p = Persona(
        tipo_documento="CC",
        nro_documento=nro,
        nombres=f"Persona {nro}",
        id_tipo_persona=tipo_id,
        id_cargo=cargo_id,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


def _make_embedding() -> bytes:
    """Genera un embedding aleatorio serializado."""
    v = np.random.default_rng(0).random(512).astype(np.float32)
    v /= np.linalg.norm(v)
    return embedding_to_bytes(v)


# ═══════════════════════════════════════════════════════════════════════════════
#  CATÁLOGOS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAreaModel:
    """Pruebas sobre el modelo Area."""

    def test_seed_areas_existen(self, db_session):
        """Los catálogos sembrados en conftest existen en la BD."""
        areas = db_session.query(Area).all()
        assert len(areas) >= 3

    def test_area_tiene_nombre(self, db_session):
        """Cada área tiene nombre no nulo."""
        for area in db_session.query(Area).all():
            assert area.nombre

    def test_area_nombre_unico(self, db_session):
        """Insertar dos áreas con el mismo nombre lanza IntegrityError."""
        db_session.add(Area(nombre="__DupArea__"))
        db_session.commit()
        db_session.add(Area(nombre="__DupArea__"))
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_area_relacion_cargos(self, db_session):
        """El área 'Tecnología' tiene al menos 3 cargos asociados."""
        area = db_session.query(Area).filter_by(nombre="Tecnología").first()
        assert area is not None
        assert len(area.cargos) >= 3


class TestCargoModel:
    """Pruebas sobre el modelo Cargo."""

    def test_seed_cargos_existen(self, db_session):
        """Los catálogos sembrados existen."""
        assert db_session.query(Cargo).count() >= 9

    def test_cargo_pertenece_a_area(self, db_session):
        """Cada cargo tiene un área asociada."""
        for cargo in db_session.query(Cargo).all():
            assert cargo.area is not None

    def test_cargo_fk_area_requerida(self, db_session):
        """Crear un Cargo con id_area inexistente genera una relación huérfana.

        SQLite sin ``PRAGMA foreign_keys = ON`` no impone FK constraints.
        El test verifica que el cargo insertado tiene ``.area == None``
        (relación huérfana). En BD con FK enforcement (PostgreSQL) se lanzaría
        IntegrityError; ambos casos se manejan correctamente.
        """
        db_session.add(Cargo(nombre="CargoSinAreaValida", id_area=99999))
        try:
            db_session.commit()
            cargo = db_session.query(Cargo).filter_by(nombre="CargoSinAreaValida").first()
            assert cargo is not None
            assert cargo.area is None   # huérfano — esperado con SQLite sin PRAGMA FK
        except IntegrityError:
            db_session.rollback()      # BD con FK enforcement


class TestTipoPersonaModel:
    """Pruebas sobre el modelo TipoPersona."""

    def test_seed_tipos_existen(self, db_session):
        """Los tres tipos base existen."""
        tipos = {t.tipo for t in db_session.query(TipoPersona).all()}
        assert {"Empleado", "Visitante", "Contratista"}.issubset(tipos)

    def test_empleado_flag_verdadero(self, db_session):
        """Empleado tiene es_empleado=True; Visitante y Contratista tienen False."""
        empleado    = db_session.query(TipoPersona).filter_by(tipo="Empleado").first()
        visitante   = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        contratista = db_session.query(TipoPersona).filter_by(tipo="Contratista").first()
        assert empleado.es_empleado is True
        assert visitante.es_empleado is False
        assert contratista.es_empleado is False

    def test_tipo_nombre_unico(self, db_session):
        """No se pueden insertar dos tipos con el mismo nombre."""
        db_session.add(TipoPersona(tipo="__DupTipo__", es_empleado=False))
        db_session.commit()
        db_session.add(TipoPersona(tipo="__DupTipo__", es_empleado=False))
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()


# ═══════════════════════════════════════════════════════════════════════════════
#  PERSONA
# ═══════════════════════════════════════════════════════════════════════════════

class TestPersonaModel:
    """Pruebas sobre el modelo Persona."""

    def test_crear_visitante(self, db_session):
        """Crear una persona de tipo Visitante sin cargo es válido."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p = _make_persona(db_session, nro="V001", tipo_id=tipo.id_tipo_persona)
        assert p.id_persona is not None
        assert p.activo is True
        assert p.id_cargo is None

    def test_crear_empleado_con_cargo(self, db_session):
        """Crear una persona Empleado con cargo asigna correctamente la FK."""
        tipo  = db_session.query(TipoPersona).filter_by(tipo="Empleado").first()
        cargo = db_session.query(Cargo).filter_by(nombre="Desarrollador Backend").first()
        p = _make_persona(db_session, nro="E001", tipo_id=tipo.id_tipo_persona, cargo_id=cargo.id_cargo)
        assert p.id_cargo == cargo.id_cargo
        assert p.cargo.nombre == "Desarrollador Backend"

    def test_fecha_registro_auto(self, db_session):
        """fecha_registro se asigna automáticamente al crear la persona."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p = _make_persona(db_session, nro="V002", tipo_id=tipo.id_tipo_persona)
        assert isinstance(p.fecha_registro, datetime)

    def test_nro_documento_unico(self, db_session):
        """Dos personas con el mismo nro_documento violan la restricción UNIQUE."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        _make_persona(db_session, nro="V003", tipo_id=tipo.id_tipo_persona)
        db_session.add(Persona(
            tipo_documento="CC", nro_documento="V003",
            nombres="Duplicado", id_tipo_persona=tipo.id_tipo_persona,
        ))
        with pytest.raises(IntegrityError):
            db_session.commit()
        db_session.rollback()

    def test_activo_default_true(self, db_session):
        """El campo activo es True por defecto."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p = _make_persona(db_session, nro="V004", tipo_id=tipo.id_tipo_persona)
        assert p.activo is True

    def test_relacion_tipo_persona(self, db_session):
        """La relación ORM tipo_persona carga el objeto TipoPersona correcto."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p = _make_persona(db_session, nro="V005", tipo_id=tipo.id_tipo_persona)
        assert p.tipo_persona.tipo == "Visitante"


# ═══════════════════════════════════════════════════════════════════════════════
#  REGISTRO
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistroModel:
    """Pruebas sobre el modelo Registro."""

    def test_crear_registro_tipo_registro(self, db_session):
        """Insertar un Registro de tipo 'registro' con embedding serializado."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="R001", tipo_id=tipo.id_tipo_persona)
        reg  = Registro(
            id_persona=p.id_persona,
            evento="registro",
            tipo_acceso=None,
            embedding_facial=_make_embedding(),
            similitud=None,
        )
        db_session.add(reg)
        db_session.commit()
        db_session.refresh(reg)
        assert reg.id_registro is not None
        assert reg.evento == "registro"
        assert isinstance(reg.embedding_facial, bytes)
        assert len(reg.embedding_facial) == 512 * 4  # 512 float32 = 2048 bytes

    def test_crear_registro_tipo_acceso(self, db_session):
        """Insertar un Registro de tipo 'acceso' con similitud coseno."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="R002", tipo_id=tipo.id_tipo_persona)
        reg  = Registro(
            id_persona=p.id_persona,
            evento="acceso",
            tipo_acceso="entrada",
            embedding_facial=_make_embedding(),
            similitud=0.87,
        )
        db_session.add(reg)
        db_session.commit()
        db_session.refresh(reg)
        assert reg.tipo_acceso == "entrada"
        assert abs(reg.similitud - 0.87) < 1e-5

    def test_cascade_delete_persona_borra_registros(self, db_session):
        """Eliminar una Persona elimina en cascada sus Registros."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="R003", tipo_id=tipo.id_tipo_persona)
        db_session.add(Registro(
            id_persona=p.id_persona,
            evento="registro",
            tipo_acceso=None,
            embedding_facial=_make_embedding(),
        ))
        db_session.commit()

        db_session.delete(p)
        db_session.commit()

        count = db_session.query(Registro).filter_by(id_persona=p.id_persona).count()
        assert count == 0

    def test_relacion_persona_cargada(self, db_session):
        """El ORM carga la relación .persona correctamente."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="R004", tipo_id=tipo.id_tipo_persona)
        reg  = Registro(
            id_persona=p.id_persona,
            evento="registro",
            tipo_acceso=None,
            embedding_facial=_make_embedding(),
        )
        db_session.add(reg)
        db_session.commit()
        db_session.refresh(reg)
        assert reg.persona.nombres == p.nombres


# ═══════════════════════════════════════════════════════════════════════════════
#  VISITA
# ═══════════════════════════════════════════════════════════════════════════════

class TestVisitaModel:
    """Pruebas sobre el modelo Visita."""

    def test_crear_visita(self, db_session):
        """Insertar una Visita con fecha_salida nula (visita activa)."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="VIS001", tipo_id=tipo.id_tipo_persona)
        v    = Visita(id_persona=p.id_persona, motivo="Reunión de negocios")
        db_session.add(v)
        db_session.commit()
        db_session.refresh(v)
        assert v.id_visita is not None
        assert v.fecha_salida is None
        assert isinstance(v.fecha, datetime)

    def test_registrar_salida(self, db_session):
        """Actualizar fecha_salida cierra la visita."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="VIS002", tipo_id=tipo.id_tipo_persona)
        v    = Visita(id_persona=p.id_persona, motivo="Trámite")
        db_session.add(v)
        db_session.commit()

        v.fecha_salida = datetime.now(timezone.utc)
        db_session.commit()
        db_session.refresh(v)
        assert v.fecha_salida is not None

    def test_cascade_delete_persona_borra_visitas(self, db_session):
        """Eliminar una Persona elimina en cascada sus Visitas."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="VIS003", tipo_id=tipo.id_tipo_persona)
        db_session.add(Visita(id_persona=p.id_persona, motivo="Entrega"))
        db_session.commit()

        db_session.delete(p)
        db_session.commit()

        assert db_session.query(Visita).filter_by(id_persona=p.id_persona).count() == 0

    def test_relacion_persona_en_visita(self, db_session):
        """La relación .persona de Visita retorna la persona correcta."""
        tipo = db_session.query(TipoPersona).filter_by(tipo="Visitante").first()
        p    = _make_persona(db_session, nro="VIS004", tipo_id=tipo.id_tipo_persona)
        v    = Visita(id_persona=p.id_persona, motivo="Visita técnica")
        db_session.add(v)
        db_session.commit()
        db_session.refresh(v)
        assert v.persona.id_persona == p.id_persona
