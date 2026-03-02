"""Configuración (variables de entorno)."""
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/app/db/sqlite.db")
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
# Umbral de similitud para reconocimiento facial (0-1; mayor = más estricto)
# Valores más bajos permiten misma persona con distinta ropa/ángulo/luz (ej. 0.45–0.55)
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.48"))
# Distancia euclidiana máxima para considerar candidato (Facenet: misma persona suele estar < 1.0–1.2)
FACE_DISTANCE_THRESHOLD = float(os.getenv("FACE_DISTANCE_THRESHOLD", "1.1"))
