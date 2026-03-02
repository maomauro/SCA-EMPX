"""Pruebas unitarias de funciones puras del pipeline ML (face_model.py).

No requiere imágenes reales ni carga de modelos pesados.
Cubre las utilidades matemáticas y de serialización:

    - cosine_similarity(a, b)
    - embedding_to_bytes(emb)
    - bytes_to_embedding(data)
    - find_best_match(query, candidates, threshold)
    - _normalize(v)
"""
from __future__ import annotations

import numpy as np
import pytest

from backend.app.ml.face_model import (
    EMBEDDING_DIM,
    EMBEDDING_DTYPE,
    _normalize,
    bytes_to_embedding,
    cosine_similarity,
    embedding_to_bytes,
    find_best_match,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _unit_vec(seed: int) -> np.ndarray:
    """Genera un vector unitario aleatorio de 512 dimensiones."""
    rng = np.random.default_rng(seed)
    v   = rng.random(EMBEDDING_DIM).astype(EMBEDDING_DTYPE)
    return v / np.linalg.norm(v)


# ═══════════════════════════════════════════════════════════════════════════════
#  _normalize
# ═══════════════════════════════════════════════════════════════════════════════

class TestNormalize:
    """Pruebas de _normalize(v)."""

    def test_norma_1_tras_normalizar(self):
        """El vector normalizado tiene norma ≈ 1."""
        v    = np.array([3.0, 4.0], dtype=np.float32)
        norm = np.linalg.norm(_normalize(v))
        assert abs(norm - 1.0) < 1e-6

    def test_vector_cero_sin_modificar(self):
        """Un vector de ceros se retorna sin modificar (evita div/0)."""
        v    = np.zeros(512, dtype=np.float32)
        out  = _normalize(v)
        assert np.allclose(out, v)

    def test_vector_512_dims(self):
        """Normalizar un vector de 512 dimensiones retorna el mismo tamaño."""
        v   = _unit_vec(0)
        out = _normalize(v * 5.0)
        assert out.shape == (EMBEDDING_DIM,)

    def test_idempotencia(self):
        """Normalizar un vector ya normalizado no lo modifica."""
        v   = _unit_vec(1)
        out = _normalize(v)
        assert np.allclose(v, out, atol=1e-6)


# ═══════════════════════════════════════════════════════════════════════════════
#  cosine_similarity
# ═══════════════════════════════════════════════════════════════════════════════

class TestCosineSimilarity:
    """Pruebas de cosine_similarity(a, b)."""

    def test_mismo_vector_similitud_1(self):
        """Un vector comparado consigo mismo da similitud = 1.0."""
        v = _unit_vec(0)
        assert abs(cosine_similarity(v, v) - 1.0) < 1e-5

    def test_vectores_ortogonales_similitud_0(self):
        """Dos vectores ortogonales dan similitud = 0.0 (recortado a 0)."""
        a = np.zeros(512, dtype=np.float32)
        b = np.zeros(512, dtype=np.float32)
        a[0], b[256] = 1.0, 1.0
        assert cosine_similarity(a, b) == pytest.approx(0.0, abs=1e-5)

    def test_similitud_en_rango_0_1(self):
        """La similitud siempre está en [0, 1]."""
        for seed in range(20):
            a = _unit_vec(seed)
            b = _unit_vec(seed + 100)
            sim = cosine_similarity(a, b)
            assert 0.0 <= sim <= 1.0, f"Similitud fuera de rango: {sim}"

    def test_similitud_simetrica(self):
        """cosine_similarity(a, b) == cosine_similarity(b, a)."""
        a = _unit_vec(7)
        b = _unit_vec(8)
        assert abs(cosine_similarity(a, b) - cosine_similarity(b, a)) < 1e-6

    def test_similitud_alta_para_vectores_cercanos(self):
        """Vectores casi iguales (con pequeño ruido) tienen similitud alta."""
        v     = _unit_vec(42)
        rng   = np.random.default_rng(42)
        noise = rng.normal(0, 0.01, size=EMBEDDING_DIM).astype(np.float32)
        v2    = _normalize(v + noise)
        assert cosine_similarity(v, v2) > 0.90

    def test_similitud_baja_para_vectores_distintos(self):
        """Dos personas distintas (vectores independientes) tienen similitud menor."""
        a = _unit_vec(1)
        b = _unit_vec(9999)
        assert cosine_similarity(a, b) < 0.95


# ═══════════════════════════════════════════════════════════════════════════════
#  embedding_to_bytes / bytes_to_embedding
# ═══════════════════════════════════════════════════════════════════════════════

class TestEmbeddingSerialization:
    """Pruebas de round-trip embedding ↔ bytes."""

    def test_roundtrip_preserva_valores(self):
        """Serializar y deserializar un embedding retorna valores idénticos."""
        emb  = _unit_vec(0)
        data = embedding_to_bytes(emb)
        emb2 = bytes_to_embedding(data)
        assert np.allclose(emb, emb2, atol=1e-7)

    def test_longitud_bytes_2048(self):
        """Un embedding de 512 float32 ocupa exactamente 2048 bytes."""
        emb  = _unit_vec(1)
        data = embedding_to_bytes(emb)
        assert len(data) == EMBEDDING_DIM * 4  # float32 = 4 bytes

    def test_tipo_retorno_es_bytes(self):
        """embedding_to_bytes retorna un objeto bytes."""
        emb  = _unit_vec(2)
        data = embedding_to_bytes(emb)
        assert isinstance(data, bytes)

    def test_tipo_retorno_es_ndarray(self):
        """bytes_to_embedding retorna un ndarray float32."""
        emb  = _unit_vec(3)
        data = embedding_to_bytes(emb)
        emb2 = bytes_to_embedding(data)
        assert isinstance(emb2, np.ndarray)
        assert emb2.dtype == EMBEDDING_DTYPE

    def test_copia_independiente(self):
        """bytes_to_embedding retorna una copia, no una vista del buffer."""
        emb  = _unit_vec(4)
        data = embedding_to_bytes(emb)
        emb2 = bytes_to_embedding(data)
        emb2[0] = 999.0
        # data no debería cambiar
        emb3 = bytes_to_embedding(data)
        assert emb3[0] != 999.0

    def test_dimension_correcta(self):
        """El array deserializado tiene exactamente 512 dimensiones."""
        emb  = _unit_vec(5)
        emb2 = bytes_to_embedding(embedding_to_bytes(emb))
        assert emb2.shape == (EMBEDDING_DIM,)


# ═══════════════════════════════════════════════════════════════════════════════
#  find_best_match
# ═══════════════════════════════════════════════════════════════════════════════

class TestFindBestMatch:
    """Pruebas de find_best_match(query, candidates, threshold)."""

    def test_lista_vacia_retorna_none(self):
        """Sin candidatos retorna None."""
        q = _unit_vec(0)
        assert find_best_match(q, [], threshold=0.5) is None

    def test_umbral_no_superado_retorna_none(self):
        """Si la mejor similitud está por debajo del umbral, retorna None."""
        q   = _unit_vec(0)
        c   = _unit_vec(99)   # vector muy diferente
        sim = cosine_similarity(q, c)
        # Usamos umbral = sim + 0.1 para garantizar que no pasa
        result = find_best_match(q, [(1, c)], threshold=min(sim + 0.1, 1.0))
        assert result is None

    def test_match_exacto(self):
        """Un candidato idéntico al query debe retornar similitud ≈ 1.0."""
        q      = _unit_vec(0)
        result = find_best_match(q, [(42, q)], threshold=0.9)
        assert result is not None
        id_p, sim = result
        assert id_p == 42
        assert sim >= 0.9999

    def test_mejor_candidato_seleccionado(self):
        """Con múltiples candidatos retorna el de mayor similitud."""
        q = _unit_vec(0)
        # candidate 2 es casi idéntico al query
        rng   = np.random.default_rng(0)
        noise = rng.normal(0, 0.01, EMBEDDING_DIM).astype(np.float32)
        c2    = _normalize(q + noise)
        c_bad = _unit_vec(9999)

        result = find_best_match(q, [(1, c_bad), (2, c2), (3, c_bad)], threshold=0.5)
        assert result is not None
        assert result[0] == 2

    def test_similitud_redondeada_a_4_decimales(self):
        """La similitud retornada tiene 4 decimales como máximo."""
        q      = _unit_vec(0)
        result = find_best_match(q, [(1, q)], threshold=0.5)
        assert result is not None
        _, sim = result
        # Verificar que es igual a round(sim, 4)
        assert sim == round(sim, 4)

    def test_umbral_exacto_pasa(self):
        """Si la similitud iguala exactamente el umbral, el match es aceptado."""
        q   = _unit_vec(0)
        sim = cosine_similarity(q, q)     # = 1.0
        result = find_best_match(q, [(7, q)], threshold=sim)
        assert result is not None

    def test_multiples_candidatos_umbral_alto(self):
        """Con umbral 0.99 solo pasa el candidato casi idéntico."""
        q      = _unit_vec(0)
        rng    = np.random.default_rng(seed=1)
        noise  = rng.normal(0, 0.001, EMBEDDING_DIM).astype(np.float32)
        near   = _normalize(q + noise)
        far1   = _unit_vec(1)
        far2   = _unit_vec(2)

        result = find_best_match(q, [(10, far1), (20, near), (30, far2)], threshold=0.99)
        assert result is not None
        assert result[0] == 20
