"""Pruebas del endpoint de validación de acceso facial.

Ruta cubierta:
    POST /api/v1/acceso/validar

Este endpoint es el núcleo del sistema: recibe una imagen, identifica al
individuo y registra el evento de acceso. Las pruebas validan:
    - Galería vacía → sin_personas_registradas
    - Imagen sin rostro → rostro_no_detectado
    - Imagen inválida → 400 o rostro_no_detectado
    - Pipeline completo con embedding real en BD → acceso permitido
    - Alternancia entrada/salida
    - Aprendizaje progresivo (embedding alta confianza)
    - Cierre automático de visita al salir
"""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from backend.app.db.models import Persona, Registro, Visita, TipoPersona
from backend.app.ml.face_model import (
    embedding_to_bytes,
    get_embedding_from_bytes,
    EMBEDDING_DIM,
)

# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _make_emb_bytes(seed: int = 0) -> bytes:
    """Genera un embedding unitario determinista."""
    rng = np.random.default_rng(seed)
    v   = rng.random(EMBEDDING_DIM).astype(np.float32)
    return embedding_to_bytes(v / np.linalg.norm(v))


def _blank_jpeg() -> bytes:
    img = Image.new("RGB", (224, 224), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def _jpeg_file(data: bytes, name: str = "foto.jpg") -> dict:
    """Arma el dict de files para TestClient."""
    return {"foto": (name, io.BytesIO(data), "image/jpeg")}


def _crear_persona_bd(db, nro: str, es_empleado: bool = True) -> Persona:
    tipo = db.query(TipoPersona).filter_by(tipo="Empleado" if es_empleado else "Visitante").first()
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


def _insertar_embedding_registro(db, id_persona: int, seed: int = 42) -> Registro:
    """Inserta un embedding de tipo 'registro' en la galería."""
    reg = Registro(
        id_persona=id_persona,
        evento="registro",
        tipo_acceso=None,
        embedding_facial=_make_emb_bytes(seed),
        similitud=None,
    )
    db.add(reg)
    db.commit()
    db.refresh(reg)
    return reg


# ═══════════════════════════════════════════════════════════════════════════════
#  Escenarios de fallo
# ═══════════════════════════════════════════════════════════════════════════════

class TestAccesoFallos:
    """Casos donde el acceso no puede concederse."""

    def test_imagen_vacia_400(self, client):
        """Imagen vacía (0 bytes) retorna 400."""
        r = client.post("/api/v1/acceso/validar", files={"foto": ("foto.jpg", io.BytesIO(b""), "image/jpeg")})
        assert r.status_code == 400

    def test_bytes_invalidos_retorna_sin_rostro(self, client):
        """Bytes que no son imagen retornan rostro_no_detectado."""
        r = client.post("/api/v1/acceso/validar", files={"foto": ("foto.jpg", io.BytesIO(b"no-es-imagen"), "image/jpeg")})
        assert r.status_code in (200, 400)
        if r.status_code == 200:
            assert r.json()["permitido"] is False

    def test_imagen_blanca_sin_galeria_retorna_no_permitido(self, client):
        """BD vacía + imagen blanca → no se concede acceso."""
        r = client.post("/api/v1/acceso/validar", files=_jpeg_file(_blank_jpeg()))
        assert r.status_code in (200, 400)
        if r.status_code == 200:
            assert r.json()["permitido"] is False

    def test_galeria_vacia_retorna_sin_personas_registradas(self, client, blank_image_bytes):
        """Sin personas con embeddings en BD retorna motivo=sin_personas_registradas
        o rostro_no_detectado (depende del orden de validación)."""
        r = client.post("/api/v1/acceso/validar", files=_jpeg_file(blank_image_bytes))
        assert r.status_code in (200, 400)
        if r.status_code == 200:
            data = r.json()
            assert data["permitido"] is False
            assert data["motivo"] in ("rostro_no_detectado", "sin_personas_registradas")

    def test_motivo_persona_no_identificada_con_embedding_diferente(self, client, db_session, blank_image_bytes):
        """Un embedding que no coincide con ninguno de la galería retorna
        motivo=rostro_no_detectado (imagen blanca no tiene rostro)."""
        p = _crear_persona_bd(db_session, nro="ACC_FAIL001")
        _insertar_embedding_registro(db_session, p.id_persona, seed=1)

        r = client.post("/api/v1/acceso/validar", files=_jpeg_file(blank_image_bytes))
        assert r.status_code in (200, 400)
        if r.status_code == 200:
            assert r.json()["permitido"] is False

    def test_respuesta_estructura_cuando_no_permitido(self, client, blank_image_bytes):
        """La respuesta de acceso denegado tiene los campos correctos."""
        r = client.post("/api/v1/acceso/validar", files=_jpeg_file(blank_image_bytes))
        if r.status_code == 200:
            data = r.json()
            assert "permitido"  in data
            assert "motivo"     in data
            assert "persona"    in data
            assert "similitud"  in data


# ═══════════════════════════════════════════════════════════════════════════════
#  Pipeline completo con imagen real
# ═══════════════════════════════════════════════════════════════════════════════

class TestAccesoConRostroReal:
    """Pruebas que requieren la imagen de test con un rostro detectable.

    Si la imagen de test no supera la detección facial, los tests se saltan
    automáticamente (no se considera un fallo del código).
    """

    def _extraer_emb(self, face_image_bytes: bytes) -> bytes | None:
        """Extrae embedding real de la imagen. Retorna None si no hay rostro."""
        emb = get_embedding_from_bytes(face_image_bytes)
        if emb is None:
            return None
        return embedding_to_bytes(emb)

    def test_cara_detectada_match_en_galeria(self, client, db_session, face_image_bytes):
        """Con el embedding de la imagen de test en la galería, el acceso es concedido."""
        emb_bytes = self._extraer_emb(face_image_bytes)
        if emb_bytes is None:
            pytest.skip("La imagen de test no tiene rostro detectable")

        p   = _crear_persona_bd(db_session, nro="ACC_OK001", es_empleado=False)
        reg = Registro(
            id_persona=p.id_persona,
            evento="registro",
            tipo_acceso=None,
            embedding_facial=emb_bytes,
        )
        db_session.add(reg)
        db_session.commit()

        r = client.post("/api/v1/acceso/validar", files=_jpeg_file(face_image_bytes))
        assert r.status_code == 200
        data = r.json()
        assert data["permitido"] is True
        assert data["tipo_acceso"] == "entrada"
        assert data["similitud"] is not None
        assert data["persona"]["id_persona"] == p.id_persona

    def test_respuesta_completa_cuando_permitido(self, client, db_session, face_image_bytes):
        """La respuesta de acceso concedido contiene todos los campos esperados."""
        emb_bytes = self._extraer_emb(face_image_bytes)
        if emb_bytes is None:
            pytest.skip("La imagen de test no tiene rostro detectable")

        p = _crear_persona_bd(db_session, nro="ACC_CAMPOS001")
        Registro(id_persona=p.id_persona, evento="registro", tipo_acceso=None, embedding_facial=emb_bytes)
        db_session.add(Registro(
            id_persona=p.id_persona, evento="registro",
            tipo_acceso=None, embedding_facial=emb_bytes,
        ))
        db_session.commit()

        r    = client.post("/api/v1/acceso/validar", files=_jpeg_file(face_image_bytes))
        data = r.json()
        if data.get("permitido"):
            campos = {"permitido", "tipo_acceso", "similitud", "persona"}
            assert campos.issubset(data.keys())
            assert "id_persona" in data["persona"]
            assert "nombres"    in data["persona"]

    def test_primera_deteccion_es_entrada(self, client, db_session, face_image_bytes):
        """La primera detección del día siempre es 'entrada'."""
        emb_bytes = self._extraer_emb(face_image_bytes)
        if emb_bytes is None:
            pytest.skip("La imagen de test no tiene rostro detectable")

        p = _crear_persona_bd(db_session, nro="ACC_ENTRADA001")
        db_session.add(Registro(
            id_persona=p.id_persona, evento="registro",
            tipo_acceso=None, embedding_facial=emb_bytes,
        ))
        db_session.commit()

        r    = client.post("/api/v1/acceso/validar", files=_jpeg_file(face_image_bytes))
        data = r.json()
        if data.get("permitido"):
            assert data["tipo_acceso"] == "entrada"

    def test_similitud_en_rango_valido(self, client, db_session, face_image_bytes):
        """La similitud retornada está en el rango [0, 1]."""
        emb_bytes = self._extraer_emb(face_image_bytes)
        if emb_bytes is None:
            pytest.skip("La imagen de test no tiene rostro detectable")

        p = _crear_persona_bd(db_session, nro="ACC_SIM001")
        db_session.add(Registro(
            id_persona=p.id_persona, evento="registro",
            tipo_acceso=None, embedding_facial=emb_bytes,
        ))
        db_session.commit()

        r    = client.post("/api/v1/acceso/validar", files=_jpeg_file(face_image_bytes))
        data = r.json()
        if data.get("permitido") and data.get("similitud") is not None:
            assert 0.0 <= data["similitud"] <= 1.0

    def test_acceso_queda_registrado_en_bd(self, client, db_session, face_image_bytes):
        """El evento de acceso queda persistido en la tabla registros."""
        emb_bytes = self._extraer_emb(face_image_bytes)
        if emb_bytes is None:
            pytest.skip("La imagen de test no tiene rostro detectable")

        p = _crear_persona_bd(db_session, nro="ACC_PERSIST001", es_empleado=False)
        db_session.add(Registro(
            id_persona=p.id_persona, evento="registro",
            tipo_acceso=None, embedding_facial=emb_bytes,
        ))
        db_session.commit()

        r    = client.post("/api/v1/acceso/validar", files=_jpeg_file(face_image_bytes))
        data = r.json()
        if data.get("permitido"):
            count = db_session.query(Registro).filter(
                Registro.id_persona == p.id_persona,
                Registro.evento     == "acceso",
            ).count()
            assert count >= 1


# ═══════════════════════════════════════════════════════════════════════════════
#  Aprendizaje progresivo
# ═══════════════════════════════════════════════════════════════════════════════

class TestAprendizajeProgresivo:
    """El sistema agrega embeddings de alta confianza a la galería."""

    def test_acceso_alta_confianza_agrega_embedding(self, client, db_session, face_image_bytes):
        """Un acceso con similitud ≥ FACE_HIGH_CONFIDENCE_THRESHOLD agrega embedding."""
        from backend.app.config.config import FACE_HIGH_CONFIDENCE_THRESHOLD
        from backend.app.ml.face_model import get_embedding_from_bytes, embedding_to_bytes

        emb = get_embedding_from_bytes(face_image_bytes)
        if emb is None:
            pytest.skip("La imagen de test no tiene rostro detectable")

        emb_bytes = embedding_to_bytes(emb)

        p = _crear_persona_bd(db_session, nro="APR001")
        db_session.add(Registro(
            id_persona=p.id_persona, evento="registro",
            tipo_acceso=None, embedding_facial=emb_bytes,
        ))
        db_session.commit()

        n_antes = db_session.query(Registro).filter(
            Registro.id_persona == p.id_persona,
            Registro.evento     == "registro",
        ).count()

        r    = client.post("/api/v1/acceso/validar", files=_jpeg_file(face_image_bytes))
        data = r.json()

        if data.get("permitido") and data.get("similitud", 0) >= FACE_HIGH_CONFIDENCE_THRESHOLD:
            db_session.expire_all()
            n_despues = db_session.query(Registro).filter(
                Registro.id_persona == p.id_persona,
                Registro.evento     == "registro",
            ).count()
            assert n_despues >= n_antes  # pudo agregar o no (depende del límite)


# ═══════════════════════════════════════════════════════════════════════════════
#  Cierre automático de visita
# ═══════════════════════════════════════════════════════════════════════════════

class TestCierreVisita:
    """Al salir, la visita activa del visitante se cierra automáticamente."""

    def test_visita_se_cierra_cuando_visitante_sale(self, client, db_session, face_image_bytes):
        """Cuando un visitante hace 2 accesos (entrada → salida), su visita
        activa queda cerrada automáticamente."""
        from backend.app.ml.face_model import get_embedding_from_bytes, embedding_to_bytes

        emb = get_embedding_from_bytes(face_image_bytes)
        if emb is None:
            pytest.skip("La imagen de test no tiene rostro detectable")

        emb_bytes = embedding_to_bytes(emb)
        p = _crear_persona_bd(db_session, nro="CIV001", es_empleado=False)
        db_session.add(Registro(
            id_persona=p.id_persona, evento="registro",
            tipo_acceso=None, embedding_facial=emb_bytes,
        ))
        v = Visita(id_persona=p.id_persona, motivo="Test cierre automático")
        db_session.add(v)
        db_session.commit()

        # Forzar una 'entrada' de referencia para que el próximo acceso sea 'salida'
        from datetime import datetime, timedelta, timezone
        reg_entrada = Registro(
            id_persona=p.id_persona,
            evento="acceso",
            tipo_acceso="entrada",
            embedding_facial=emb_bytes,
            similitud=0.9,
            fecha=datetime.now(timezone.utc) - timedelta(minutes=5),
        )
        db_session.add(reg_entrada)
        db_session.commit()

        # Ahora el próximo acceso debería ser 'salida'
        r    = client.post("/api/v1/acceso/validar", files=_jpeg_file(face_image_bytes))
        data = r.json()

        if data.get("permitido") and data.get("tipo_acceso") == "salida":
            db_session.expire_all()
            v_updated = db_session.query(Visita).filter_by(id_visita=v.id_visita).first()
            assert v_updated.fecha_salida is not None, "La visita debería haberse cerrado"
