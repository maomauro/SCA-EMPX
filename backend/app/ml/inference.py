"""
Detección de rostro, generación de embedding y comparación.
HU-05: validar acceso por reconocimiento facial.
Usa DeepFace (Facenet, 128-d) para compatibilidad con Windows sin CMake/dlib.
"""
from __future__ import annotations

import io
from typing import Tuple

import numpy as np
from PIL import Image
from deepface import DeepFace

# Facenet retorna 128 dimensiones
EMBEDDING_DTYPE = np.float64
EMBEDDING_SHAPE = (128,)

# Modelo DeepFace: Facenet da embeddings 128-d (compatible con comparación euclidiana)
MODEL_NAME = "Facenet"


def image_bytes_to_array(image_bytes: bytes) -> np.ndarray:
    """Convierte bytes a array RGB (BGR para OpenCV/DeepFace)."""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert("RGB")
    return np.array(img)[:, :, ::-1]  # RGB -> BGR


def get_embedding_from_image(image_bytes: bytes) -> np.ndarray | None:
    """
    Detecta un rostro en la imagen y retorna su embedding (128-d con Facenet).
    Retorna None si no se detecta exactamente un rostro.
    """
    arr = image_bytes_to_array(image_bytes)
    try:
        result = DeepFace.represent(arr, model_name=MODEL_NAME, enforce_detection=True)
    except Exception:
        return None
    if not result or len(result) != 1:
        return None
    embedding = np.array(result[0]["embedding"], dtype=EMBEDDING_DTYPE)
    return embedding


def embedding_to_bytes(embedding: np.ndarray) -> bytes:
    """Serializa embedding a bytes para guardar en BD."""
    return embedding.astype(EMBEDDING_DTYPE).tobytes()


def bytes_to_embedding(data: bytes) -> np.ndarray:
    """Deserializa bytes de BD a embedding numpy."""
    return np.frombuffer(data, dtype=EMBEDDING_DTYPE).reshape(EMBEDDING_SHAPE)


def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.linalg.norm(a - b))


def face_distance_to_similarity(distance: float) -> float:
    """Convierte distancia euclidiana a similitud en [0, 1]."""
    return 1.0 / (1.0 + float(distance))


def find_best_match(
    query_embedding: np.ndarray,
    candidates: list[Tuple[int, np.ndarray]],
    distance_threshold: float = 0.6,
) -> Tuple[int, float] | None:
    """
    Busca la mejor coincidencia por distancia euclidiana.
    distance_threshold: máxima distancia para considerar match (Facenet: típico 0.6–1.0).
    Retorna (id_persona, similarity) o None.
    """
    if not candidates:
        return None
    best_id = None
    best_distance = float("inf")
    for person_id, emb in candidates:
        d = euclidean_distance(query_embedding, emb)
        if d < best_distance:
            best_distance = d
            best_id = person_id
    if best_id is None or best_distance > distance_threshold:
        return None
    similarity = face_distance_to_similarity(best_distance)
    return (best_id, similarity)
