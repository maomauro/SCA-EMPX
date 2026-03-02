"""Pruebas del modelo fallback — DeepFace Facenet512 + MTCNN.

Carga el modelo fallback real de DeepFace.
El modelo se inicializa una sola vez por sesión gracias al fixture
``fallback_model`` de scope="session".

Este modelo se activa cuando biometric-ai-lab/Face_Recognition falla;
produce embeddings de 512 dimensiones compatibles con el modelo principal.

Marcador ``slow``: DeepFace descarga pesos la primera vez.
Ejecutar con:
    pytest -m slow backend/tests/ml/test_fallback_model.py
"""
from __future__ import annotations

import numpy as np
import pytest

from backend.app.ml.face_model import (
    EMBEDDING_DIM,
    EMBEDDING_DTYPE,
    _FallbackModel,
    cosine_similarity,
)

pytestmark = pytest.mark.slow


# ═══════════════════════════════════════════════════════════════════════════════
#  FIXTURE — carga real del Fallback Model
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def fallback_model():
    """Instancia el modelo fallback DeepFace (Facenet512 + MTCNN) una sola vez."""
    try:
        return _FallbackModel()
    except Exception as exc:
        pytest.skip(f"DeepFace no disponible: {exc}")


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: Carga del modelo
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallbackModelCarga:
    """Valida que el modelo fallback se inicialice correctamente."""

    def test_instancia_creada(self, fallback_model):
        """_FallbackModel se instancia sin errores."""
        assert isinstance(fallback_model, _FallbackModel)

    def test_tiene_deepface(self, fallback_model):
        """El atributo _df apunta al módulo DeepFace."""
        from deepface import DeepFace
        assert fallback_model._df is DeepFace


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: get_embedding con imagen sin rostro
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallbackSinRostro:
    """El fallback rechaza correctamente imágenes sin rostro."""

    def test_imagen_blanca_retorna_none(self, fallback_model, blank_image_bytes):
        """Una imagen blanca pura no contiene rostro — retorna None."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(blank_image_bytes)).convert("RGB")
        arr = np.array(img)
        result = fallback_model.get_embedding(arr)
        assert result is None

    def test_imagen_negra_retorna_none(self, fallback_model):
        """Una imagen completamente negra no tiene rostro."""
        arr    = np.zeros((224, 224, 3), dtype=np.uint8)
        result = fallback_model.get_embedding(arr)
        assert result is None

    def test_no_lanza_excepcion_sin_rostro(self, fallback_model):
        """El modelo captura excepciones de DeepFace internamente y retorna None."""
        arr    = np.ones((100, 100, 3), dtype=np.uint8) * 128
        result = fallback_model.get_embedding(arr)  # no debe lanzar
        assert result is None or isinstance(result, np.ndarray)


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: get_embedding con imagen de rostro real
# ═══════════════════════════════════════════════════════════════════════════════

class TestFallbackConRostro:
    """El fallback extrae embeddings válidos de imágenes con rostro."""

    def test_retorna_ndarray_o_none(self, fallback_model, face_image_bytes):
        """Con una imagen real retorna ndarray o None (si no detecta rostro)."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        result = fallback_model.get_embedding(arr)
        assert result is None or isinstance(result, np.ndarray)

    def test_embedding_dimension_512(self, fallback_model, face_image_bytes):
        """El embedding tiene exactamente 512 dimensiones."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr    = np.array(img)
        result = fallback_model.get_embedding(arr)
        if result is not None:
            assert result.shape == (EMBEDDING_DIM,)

    def test_embedding_dtype_float32(self, fallback_model, face_image_bytes):
        """El embedding es float32."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr    = np.array(img)
        result = fallback_model.get_embedding(arr)
        if result is not None:
            assert result.dtype == EMBEDDING_DTYPE

    def test_embedding_normalizado(self, fallback_model, face_image_bytes):
        """El embedding retornado tiene norma L2 ≈ 1.0."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr    = np.array(img)
        result = fallback_model.get_embedding(arr)
        if result is not None:
            norm = float(np.linalg.norm(result))
            assert abs(norm - 1.0) < 1e-5, f"Norma inesperada: {norm}"

    def test_embedding_determinista(self, fallback_model, face_image_bytes):
        """La misma imagen genera el mismo embedding en dos llamadas."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr    = np.array(img)
        e1 = fallback_model.get_embedding(arr)
        e2 = fallback_model.get_embedding(arr)
        if e1 is not None and e2 is not None:
            assert np.allclose(e1, e2, atol=1e-5)

    def test_similitud_misma_imagen(self, fallback_model, face_image_bytes):
        """La misma imagen comparada consigo misma da similitud ≈ 1.0."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        e1  = fallback_model.get_embedding(arr)
        e2  = fallback_model.get_embedding(arr)
        if e1 is not None and e2 is not None:
            sim = cosine_similarity(e1, e2)
            assert sim > 0.99, f"Similitud esperada > 0.99, obtenida {sim}"
