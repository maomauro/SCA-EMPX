"""Utilidades puras del pipeline ML (solo numpy, sin torch).

Usado por tests unitarios en CI donde no se instala el extra [ml].
face_model.py importa y re-exporta estas funciones para la API.
"""
from __future__ import annotations

from typing import Optional

import numpy as np

EMBEDDING_DIM   = 512
EMBEDDING_DTYPE = np.float32


def _normalize(v: np.ndarray) -> np.ndarray:
    """Normaliza un vector a norma unitaria (L2)."""
    norm = np.linalg.norm(v)
    return v / norm if norm > 0 else v


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Similitud coseno entre dos embeddings normalizados (producto punto en [0,1])."""
    return float(np.clip(np.dot(a, b), 0.0, 1.0))


def embedding_to_bytes(emb: np.ndarray) -> bytes:
    """Serializa un embedding a bytes para persistir en BD (2048 bytes)."""
    return emb.astype(EMBEDDING_DTYPE).tobytes()


def bytes_to_embedding(data: bytes) -> np.ndarray:
    """Deserializa bytes de BD a array de embedding (512-d float32)."""
    return np.frombuffer(data, dtype=EMBEDDING_DTYPE).copy()


def find_best_match(
    query: np.ndarray,
    candidates: list[tuple[int, np.ndarray]],
    threshold: float,
) -> Optional[tuple[int, float]]:
    """Mejor coincidencia por similitud coseno; retorna (id_persona, sim) o None."""
    if not candidates:
        return None
    best_id  = None
    best_sim = -1.0
    for person_id, emb in candidates:
        sim = cosine_similarity(query, emb)
        if sim > best_sim:
            best_sim = sim
            best_id  = person_id
    if best_id is None or best_sim < threshold:
        return None
    return (best_id, round(best_sim, 4))
