"""Configuración (variables de entorno)."""
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/app/db/sqlite.db")
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
