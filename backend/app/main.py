"""
Punto de entrada de la API del Sistema de Control de Acceso (SCA-EMPX).
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from backend.app.api.v1 import api_router

app = FastAPI(
    title="SCA-EMPX API",
    description="Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas - STI S.A.S.",
    version="0.1.0",
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    """Health check."""
    return {"app": "SCA-EMPX", "status": "ok"}


@app.get("/health")
def health():
    """Salud para despliegue."""
    return {"status": "healthy"}


@app.get("/validate-access")
def validate_access_page():
    """Página de prueba para validar acceso por reconocimiento facial (HU-05)."""
    path = Path(__file__).parent / "static" / "validate-access.html"
    return FileResponse(path)
