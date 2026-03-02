"""Configuración central — variables de entorno con defaults."""
import os

# Base de datos
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/app/db/sca.db")

# Seguridad
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ── Reconocimiento facial ──────────────────────────────────────────────────
# Similitud coseno mínima para considerar match (escala 0–1, mayor = más estricto)
# Misma persona fotos distintas: típico 0.6–0.85
# Personas distintas:            típico 0.1–0.5
# 0.6 es un buen punto de partida; subir a 0.7 si hay falsos positivos.
FACE_SIMILARITY_THRESHOLD = float(os.getenv("FACE_SIMILARITY_THRESHOLD", "0.60"))

# Similitud mínima para considerar el match "de alta confianza"
# y almacenar el embedding del acceso como nuevo registro de referencia.
# Aprendizaje progresivo: solo aprende de validaciones muy seguras.
FACE_HIGH_CONFIDENCE_THRESHOLD = float(os.getenv("FACE_HIGH_CONFIDENCE_THRESHOLD", "0.80"))

# Máximo de embeddings de referencia por persona.
# Evita que con el tiempo la comparación se vuelva lenta.
MAX_EMBEDDINGS_PER_PERSONA = int(os.getenv("MAX_EMBEDDINGS_PER_PERSONA", "20"))

# Segundos entre capturas durante el registro facial
REGISTRO_CAPTURE_INTERVAL_MS = int(os.getenv("REGISTRO_CAPTURE_INTERVAL_MS", "1000"))

# Tiempo total de captura en registro (ms)
REGISTRO_CAPTURE_DURATION_MS = int(os.getenv("REGISTRO_CAPTURE_DURATION_MS", "8000"))

# Tiempo máximo de espera para detectar rostro fijo en acceso (ms)
ACCESO_DETECT_WAIT_MS = int(os.getenv("ACCESO_DETECT_WAIT_MS", "1000"))

# Debug
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
