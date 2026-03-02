"""Pruebas de los endpoints de eventos — /api/v1/events/*.

Rutas cubiertas:
    GET /api/v1/events/       → lista paginada con filtro por tipo
    GET /api/v1/events/hoy    → conteo de accesos del día actual
"""
from __future__ import annotations

import numpy as np

from backend.app.db.models import Persona, Registro, TipoPersona
from backend.app.ml.face_model import embedding_to_bytes


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _make_emb() -> bytes:
    """Genera un embedding aleatorio serializado para insertar en BD."""
    rng = np.random.default_rng(0)
    v   = rng.random(512).astype(np.float32)
    v  /= np.linalg.norm(v)
    return embedding_to_bytes(v)


def _insertar_acceso(db, id_persona: int, tipo_acceso: str, similitud: float = 0.85):
    """Inserta un registro de acceso directamente en la BD de test."""
    reg = Registro(
        id_persona=id_persona,
        evento="acceso",
        tipo_acceso=tipo_acceso,
        embedding_facial=_make_emb(),
        similitud=similitud,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


def _crear_persona_en_bd(db, nro: str) -> Persona:
    """Crea una persona visitante directamente en la BD de test."""
    tipo = db.query(TipoPersona).filter_by(tipo="Visitante").first()
    p    = Persona(
        tipo_documento="CC",
        nro_documento=nro,
        nombres=f"Persona {nro}",
        id_tipo_persona=tipo.id_tipo_persona,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return p


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/events/
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarEventos:
    """Pruebas del endpoint GET /api/v1/events/."""

    def test_status_200_sin_datos(self, client):
        """Sin eventos retorna 200 con lista vacía."""
        r = client.get("/api/v1/events/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_evento_aparece_en_lista(self, client, db_session):
        """Un registro de acceso insertado aparece en el listado."""
        p = _crear_persona_en_bd(db_session, nro="EVT001")
        _insertar_acceso(db_session, p.id_persona, "entrada")

        r = client.get("/api/v1/events/")
        ids = [e["id_persona"] for e in r.json()]
        assert p.id_persona in ids

    def test_campos_respuesta(self, client, db_session):
        """Cada evento incluye los campos requeridos."""
        p = _crear_persona_en_bd(db_session, nro="EVT002")
        _insertar_acceso(db_session, p.id_persona, "entrada")

        r = client.get("/api/v1/events/")
        campos = {"id_registro", "id_persona", "nombres", "tipo_acceso", "similitud", "fecha"}
        for ev in r.json():
            assert campos.issubset(ev.keys())
            break

    def test_filtro_tipo_entrada(self, client, db_session):
        """?tipo=entrada retorna solo eventos de entrada."""
        p = _crear_persona_en_bd(db_session, nro="EVT003")
        _insertar_acceso(db_session, p.id_persona, "entrada")
        _insertar_acceso(db_session, p.id_persona, "salida")

        r = client.get("/api/v1/events/?tipo=entrada")
        assert r.status_code == 200
        for ev in r.json():
            assert ev["tipo_acceso"] == "entrada"

    def test_filtro_tipo_salida(self, client, db_session):
        """?tipo=salida retorna solo eventos de salida."""
        p = _crear_persona_en_bd(db_session, nro="EVT004")
        _insertar_acceso(db_session, p.id_persona, "entrada")
        _insertar_acceso(db_session, p.id_persona, "salida")

        r = client.get("/api/v1/events/?tipo=salida")
        for ev in r.json():
            assert ev["tipo_acceso"] == "salida"

    def test_filtro_tipo_invalido_retorna_todos(self, client, db_session):
        """?tipo=invalido retorna todos los eventos (sin filtro)."""
        p = _crear_persona_en_bd(db_session, nro="EVT005")
        _insertar_acceso(db_session, p.id_persona, "entrada")
        _insertar_acceso(db_session, p.id_persona, "salida")

        r_todos   = client.get("/api/v1/events/")
        r_invalido = client.get("/api/v1/events/?tipo=invalido")
        # Ambos deben retornar la misma cantidad
        assert len(r_invalido.json()) == len(r_todos.json())

    def test_paginacion_limit(self, client, db_session):
        """El parámetro limit restringe la cantidad de resultados."""
        p = _crear_persona_en_bd(db_session, nro="PAG001")
        for tipo in ("entrada", "salida") * 5:
            _insertar_acceso(db_session, p.id_persona, tipo)

        r = client.get("/api/v1/events/?limit=3")
        assert r.status_code == 200
        assert len(r.json()) <= 3

    def test_paginacion_offset(self, client, db_session):
        """El parámetro offset desplaza los resultados."""
        p = _crear_persona_en_bd(db_session, nro="PAG002")
        for i in range(5):
            _insertar_acceso(db_session, p.id_persona, "entrada")

        r_all    = client.get("/api/v1/events/")
        r_offset = client.get("/api/v1/events/?offset=2")
        assert len(r_offset.json()) == len(r_all.json()) - 2

    def test_limit_invalido_422(self, client):
        """Un limit=0 (fuera del rango ge=1) retorna 422."""
        r = client.get("/api/v1/events/?limit=0")
        assert r.status_code == 422

    def test_limit_maximo_500(self, client, db_session):
        """limit=500 es el máximo permitido y retorna 200."""
        r = client.get("/api/v1/events/?limit=500")
        assert r.status_code == 200

    def test_limit_sobre_maximo_422(self, client):
        """limit=501 supera el máximo y retorna 422."""
        r = client.get("/api/v1/events/?limit=501")
        assert r.status_code == 422

    def test_solo_eventos_de_acceso_sin_registros(self, client, db_session):
        """Los registros de tipo 'registro' (alta de embedding) no aparecen."""
        p = _crear_persona_en_bd(db_session, nro="EVT_REG001")
        reg = Registro(
            id_persona=p.id_persona,
            evento="registro",       # tipo 'registro', NO 'acceso'
            tipo_acceso=None,
            embedding_facial=_make_emb(),
        )
        db_session.add(reg)
        db_session.commit()

        r = client.get("/api/v1/events/")
        for ev in r.json():
            assert ev["tipo_acceso"] in ("entrada", "salida")

    def test_similitud_en_respuesta(self, client, db_session):
        """La similitud del acceso se incluye en la respuesta."""
        p = _crear_persona_en_bd(db_session, nro="SIM001")
        _insertar_acceso(db_session, p.id_persona, "entrada", similitud=0.92)

        r   = client.get("/api/v1/events/")
        ev  = next(e for e in r.json() if e["id_persona"] == p.id_persona)
        assert abs(ev["similitud"] - 0.92) < 1e-3

    def test_orden_descendente_por_fecha(self, client, db_session):
        """Los eventos vienen ordenados del más reciente al más antiguo."""
        p = _crear_persona_en_bd(db_session, nro="ORD_EVT001")
        _insertar_acceso(db_session, p.id_persona, "entrada")
        _insertar_acceso(db_session, p.id_persona, "salida")

        r      = client.get("/api/v1/events/?limit=10")
        fechas = [e["fecha"] for e in r.json()]
        assert fechas == sorted(fechas, reverse=True)


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/events/hoy
# ═══════════════════════════════════════════════════════════════════════════════

class TestAccesosHoy:
    """Pruebas del endpoint GET /api/v1/events/hoy."""

    def test_status_200(self, client):
        """Retorna HTTP 200."""
        r = client.get("/api/v1/events/hoy")
        assert r.status_code == 200

    def test_campos_respuesta(self, client):
        """La respuesta incluye 'fecha' y 'total'."""
        r    = client.get("/api/v1/events/hoy")
        data = r.json()
        assert "fecha" in data
        assert "total" in data

    def test_total_es_entero_no_negativo(self, client):
        """El campo total es un entero ≥ 0."""
        r     = client.get("/api/v1/events/hoy")
        total = r.json()["total"]
        assert isinstance(total, int)
        assert total >= 0

    def test_fecha_formato_yyyy_mm_dd(self, client):
        """La fecha en la respuesta tiene formato YYYY-MM-DD."""
        r     = client.get("/api/v1/events/hoy")
        fecha = r.json()["fecha"]
        import re
        assert re.match(r"\d{4}-\d{2}-\d{2}", fecha)

    def test_total_incrementa_con_nuevo_acceso(self, client, db_session):
        """Insertar un acceso hoy incrementa el total."""
        r0    = client.get("/api/v1/events/hoy")
        total0 = r0.json()["total"]

        p = _crear_persona_en_bd(db_session, nro="HOY001")
        _insertar_acceso(db_session, p.id_persona, "entrada")

        r1     = client.get("/api/v1/events/hoy")
        total1 = r1.json()["total"]
        assert total1 == total0 + 1
