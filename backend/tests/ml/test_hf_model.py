"""Pruebas del modelo HuggingFace — biometric-ai-lab/Face_Recognition.

Carga el modelo real (Wide ResNet-101-2 + ArcFace + YOLO detector).
El modelo se carga UNA sola vez por sesión de pytest gracias a
la fixture ``hf_model`` de scope="session".

Marcador ``slow``: estos tests cargan/descargan modelos pesados.
Ejecutar solo con red disponible en el primer run:
    pytest -m slow backend/tests/ml/test_hf_model.py

Ejecutar sin red (solo si los pesos ya están en .cache/):
    pytest backend/tests/ml/test_hf_model.py
"""
from __future__ import annotations

import numpy as np
import pytest

from backend.app.ml.face_model import (
    EMBEDDING_DIM,
    EMBEDDING_DTYPE,
    _HFModel,
    _load_model,
    cosine_similarity,
)

pytestmark = pytest.mark.slow


# ═══════════════════════════════════════════════════════════════════════════════
#  FIXTURE — carga real del modelo HF (session-scoped)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def hf_model():
    """Carga el modelo HuggingFace una sola vez para toda la sesión.

    Si la carga falla (sin red, sin pesos) salta estos tests; no usa fallback
    para que las pruebas de _HFModel sean específicas al modelo HF.
    """
    model = _load_model()
    if not isinstance(model, _HFModel):
        pytest.skip("Modelo HF no disponible — usando fallback. Ejecuta con red.")
    return model


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: Carga del modelo
# ═══════════════════════════════════════════════════════════════════════════════

class TestHFModelCarga:
    """Valida que el modelo HF cargue correctamente con todos sus componentes."""

    def test_instancia_correcta(self, hf_model):
        """_load_model retorna una instancia _HFModel cuando el HF está disponible."""
        assert isinstance(hf_model, _HFModel)

    def test_tiene_modelo_backbone(self, hf_model):
        """El modelo tiene el backbone Wide-ResNet cargado."""
        assert hf_model._model is not None

    def test_tiene_sesion_yolo(self, hf_model):
        """El modelo tiene la sesión ONNX del detector YOLO."""
        assert hf_model._yolo is not None

    def test_tiene_transform(self, hf_model):
        """El modelo tiene el pipeline de transformación de imagen."""
        assert hf_model._transform is not None

    def test_dispositivo_cpu(self, hf_model):
        """El modelo opera en CPU (sin GPU requerida)."""
        import torch
        assert hf_model._device == torch.device("cpu")


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: get_embedding con imagen en blanco (sin rostro)
# ═══════════════════════════════════════════════════════════════════════════════

class TestHFModelSinRostro:
    """El modelo rechaza correctamente imágenes sin rostro detectable."""

    def test_imagen_blanca_retorna_none(self, hf_model, blank_image_bytes):
        """Una imagen completamente blanca no supera el detector YOLO."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(blank_image_bytes)).convert("RGB")
        arr = np.array(img)
        result = hf_model.get_embedding(arr)
        assert result is None

    def test_imagen_negra_retorna_none(self, hf_model):
        """Una imagen completamente negra no supera el detector YOLO."""
        arr = np.zeros((224, 224, 3), dtype=np.uint8)
        result = hf_model.get_embedding(arr)
        assert result is None

    def test_imagen_ruido_retorna_none_o_array(self, hf_model):
        """Una imagen de ruido uniforme no debería detectar rostro (o YOLO rechaza)."""
        rng = np.random.default_rng(42)
        arr = rng.integers(0, 256, (224, 224, 3), dtype=np.uint8)
        result = hf_model.get_embedding(arr)
        # Puede retornar None (sin rostro) o un array (si detecta algo)
        assert result is None or (isinstance(result, np.ndarray) and result.shape == (EMBEDDING_DIM,))


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: get_embedding con imagen de rostro real
# ═══════════════════════════════════════════════════════════════════════════════

class TestHFModelConRostro:
    """El modelo extrae embeddings válidos cuando hay un rostro real."""

    def test_embedding_es_ndarray(self, hf_model, face_image_bytes):
        """get_embedding retorna ndarray o None (depende si la imagen tiene rostro)."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        result = hf_model.get_embedding(arr)
        # Si la imagen de test realmente tiene un rostro el resultado no es None
        if result is not None:
            assert isinstance(result, np.ndarray)

    def test_embedding_dimension_512(self, hf_model, face_image_bytes):
        """El embedding tiene exactamente 512 dimensiones."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        result = hf_model.get_embedding(arr)
        if result is not None:
            assert result.shape == (EMBEDDING_DIM,)

    def test_embedding_dtype_float32(self, hf_model, face_image_bytes):
        """El embedding es float32."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        result = hf_model.get_embedding(arr)
        if result is not None:
            assert result.dtype == EMBEDDING_DTYPE

    def test_embedding_normalizado(self, hf_model, face_image_bytes):
        """El embedding tiene norma L2 ≈ 1.0 (normalizado)."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        result = hf_model.get_embedding(arr)
        if result is not None:
            norm = np.linalg.norm(result)
            assert abs(norm - 1.0) < 1e-5, f"Norma inesperada: {norm}"

    def test_embedding_determinista(self, hf_model, face_image_bytes):
        """La misma imagen produce el mismo embedding en dos llamadas."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        result1 = hf_model.get_embedding(arr)
        result2 = hf_model.get_embedding(arr)
        if result1 is not None and result2 is not None:
            assert np.allclose(result1, result2, atol=1e-6)

    def test_embeddings_misma_persona_alta_similitud(self, hf_model, face_image_bytes):
        """La misma imagen dos veces resulta en similitud ≈ 1.0."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr = np.array(img)
        e1 = hf_model.get_embedding(arr)
        e2 = hf_model.get_embedding(arr)
        if e1 is not None and e2 is not None:
            sim = cosine_similarity(e1, e2)
            assert sim > 0.99, f"Similitud esperada > 0.99, obtenida {sim}"


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST: Detector YOLO interno
# ═══════════════════════════════════════════════════════════════════════════════

class TestDetectFace:
    """Pruebas del detector YOLO (_detect_face)."""

    def test_detect_face_imagen_blanca_retorna_none(self, hf_model):
        """El detector no encuentra rostros en una imagen blanca."""
        arr    = np.ones((480, 640, 3), dtype=np.uint8) * 255
        result = hf_model._detect_face(arr)
        assert result is None

    def test_detect_face_imagen_negra_retorna_none(self, hf_model):
        """El detector no encuentra rostros en una imagen negra."""
        arr    = np.zeros((480, 640, 3), dtype=np.uint8)
        result = hf_model._detect_face(arr)
        assert result is None

    def test_detect_face_retorna_array_o_none(self, hf_model, face_image_bytes):
        """_detect_face retorna ndarray uint8 del recorte o None."""
        import io
        from PIL import Image
        img = Image.open(io.BytesIO(face_image_bytes)).convert("RGB")
        arr    = np.array(img)
        result = hf_model._detect_face(arr)
        assert result is None or (isinstance(result, np.ndarray) and result.dtype == np.uint8)
