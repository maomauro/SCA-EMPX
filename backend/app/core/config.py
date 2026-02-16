"""Configuración (variables de entorno)."""
import os

DEBUG = os.getenv("DEBUG", "false").lower() == "true"
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./backend/app/db/sqlite.db")
SECRET_KEY = os.getenv("SECRET_KEY", "cambiar-en-produccion")
