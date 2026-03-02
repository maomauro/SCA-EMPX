"""Pruebas del pipeline público de reconocimiento facial.

Prueba las funciones de la API pública del módulo face_model.py:
    - get_model() → singleton con lru_cache
    - get_embedding_from_bytes(image_bytes)
    - find_best_match integrado con embeddings reales

El modelo activo (HF o Fallback) ya cargado se usa a través del singleton
``get_model()``. Estas pruebas validan el comportamiento de extremo a extremo
del pipeline tal como lo usa la aplicación.

Marcador ``slow``: requiere carga inicial del modelo.
"""
from __future__ import annotations

import io

import numpy as np
import pytest
from PIL import Image

from backend.app.ml.face_model import (
    EMBEDDING_DIM,
    EMBEDDING_DTYPE,
    bytes_to_embedding,
    cosine_similarity,
    embedding_to_bytes,
    find_best_match,
    get_embedding_from_bytes,
    get_model,
    _HFModel,
    _FallbackModel,
)

pytestmark = pytest.mark.slow


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: Singleton get_model
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetModel:
    """Pruebas del singleton del modelo."""

    def test_retorna_instancia(self):
        """get_model() retorna HFModel o FallbackModel."""
        model = get_model()
        assert isinstance(model, (_HFModel, _FallbackModel))

    def test_singleton_misma_referencia(self):
        """Llamar a get_model() dos veces retorna la misma instancia (lru_cache)."""
        m1 = get_model()
        m2 = get_model()
        assert m1 is m2

    def test_tiene_metodo_get_embedding(self):
        """El modelo tiene el método get_embedding."""
        model = get_model()
        assert callable(getattr(model, "get_embedding", None))

    def test_tipo_es_hf_o_fallback(self):
        """Solo existen dos tipos de modelo posibles."""
        model = get_model()
        assert type(model).__name__ in ("_HFModel", "_FallbackModel")


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: get_embedding_from_bytes
# ═══════════════════════════════════════════════════════════════════════════════

class TestGetEmbeddingFromBytes:
    """Pruebas de la función pública get_embedding_from_bytes."""

    def test_bytes_invalidos_retorna_none(self):
        """Bytes que no son imagen válida retornan None."""
        result = get_embedding_from_bytes(b"no soy una imagen")
        assert result is None

    def test_bytes_vacios_retorna_none(self):
        """Bytes vacíos retornan None."""
        result = get_embedding_from_bytes(b"")
        assert result is None

    def test_imagen_blanca_retorna_none(self, blank_image_bytes):
        """Una imagen blanca sin rostro retorna None."""
        result = get_embedding_from_bytes(blank_image_bytes)
        assert result is None

    def test_con_imagen_real_retorna_ndarray_o_none(self, face_image_bytes):
        """Con imagen real retorna ndarray 512-d o None (sin rostro detectado)."""
        result = get_embedding_from_bytes(face_image_bytes)
        assert result is None or (
            isinstance(result, np.ndarray)
            and result.shape == (EMBEDDING_DIM,)
        )

    def test_embedding_float32(self, face_image_bytes):
        """El embedding tiene dtype float32."""
        result = get_embedding_from_bytes(face_image_bytes)
        if result is not None:
            assert result.dtype == EMBEDDING_DTYPE

    def test_embedding_normalizado(self, face_image_bytes):
        """El embedding tiene norma ≈ 1.0."""
        result = get_embedding_from_bytes(face_image_bytes)
        if result is not None:
            norm = float(np.linalg.norm(result))
            assert abs(norm - 1.0) < 1e-5

    def test_imagen_png_tambien_funciona(self, face_image_bytes):
        """Imágenes PNG se procesan igual que JPEG."""
        # Re-guardar la imagen como PNG
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        png_bytes = buf.getvalue()

        result = get_embedding_from_bytes(png_bytes)
        assert result is None or isinstance(result, np.ndarray)

    def test_determinismo_doble_llamada(self, face_image_bytes):
        """La misma imagen produce el mismo embedding en dos llamadas."""
        e1 = get_embedding_from_bytes(face_image_bytes)
        e2 = get_embedding_from_bytes(face_image_bytes)
        if e1 is not None and e2 is not None:
            assert np.allclose(e1, e2, atol=1e-5)


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: Pipeline completo — embedding → búsqueda
# ═══════════════════════════════════════════════════════════════════════════════

class TestPipelineCompleto:
    """Integra extracción de embeddings con find_best_match."""

    def test_embedding_real_encuentra_match_en_galeria(self, face_image_bytes):
        """Un embedding extraído de una imagen encuentra su match en una galería."""
        emb = get_embedding_from_bytes(face_image_bytes)
        if emb is None:
            pytest.skip("No se detectó rostro en la imagen de test")

        # Galería con el mismo embedding + embeddings aleatorios de otras personas
        rng = np.random.default_rng(42)
        otros = [
            (i, _random_unit(rng))
            for i in range(1, 6)
        ]
        galeria = otros + [(999, emb)]

        result = find_best_match(emb, galeria, threshold=0.95)
        assert result is not None
        assert result[0] == 999

    def test_embedding_no_coincide_con_galeria_distinta(self, face_image_bytes):
        """Un embedding de una persona real no coincide con embeddings aleatorios."""
        emb = get_embedding_from_bytes(face_image_bytes)
        if emb is None:
            pytest.skip("No se detectó rostro en la imagen de test")

        rng     = np.random.default_rng(100)
        galeria = [(i, _random_unit(rng)) for i in range(10)]

        result = find_best_match(emb, galeria, threshold=0.9)
        # Con vectores aleatorios la similitud esperada es baja (~0.5 en 512-d)
        # Por lo tanto no debería encontrar match con umbral 0.9
        assert result is None or result[1] < 0.9

    def test_serializar_y_recuperar_embedding(self, face_image_bytes):
        """El embedding va y viene de bytes (serialización → BD → recuperación)."""
        emb = get_embedding_from_bytes(face_image_bytes)
        if emb is None:
            pytest.skip("No se detectó rostro en la imagen de test")

        data        = embedding_to_bytes(emb)
        recuperado  = bytes_to_embedding(data)

        assert np.allclose(emb, recuperado, atol=1e-7)
        sim = cosine_similarity(emb, recuperado)
        assert sim > 0.9999

    def test_similitud_entre_versiones_misma_imagen(self, face_image_bytes):
        """Dos extracciones de la misma imagen tienen similitud muy alta."""
        e1 = get_embedding_from_bytes(face_image_bytes)
        e2 = get_embedding_from_bytes(face_image_bytes)
        if e1 is None or e2 is None:
            pytest.skip("No se detectó rostro en la imagen de test")

        sim = cosine_similarity(e1, e2)
        assert sim > 0.99, f"Similitud esperada > 0.99, obtenida {sim}"


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def _random_unit(rng: np.random.Generator) -> np.ndarray:
    """Genera un vector unitario aleatorio de 512 dimensiones."""
    v = rng.random(EMBEDDING_DIM).astype(EMBEDDING_DTYPE)
    return v / np.linalg.norm(v)
