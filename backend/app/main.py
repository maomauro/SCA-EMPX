"""
Punto de entrada de la API del Sistema de Control de Acceso (SCA-EMPX).
"""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse

from backend.app.api.v1 import api_router
from backend.app.db.database import (
    ensure_registro_acceso_schema,
    ensure_persona_visitante_columns,
    ensure_autorizacion_table,
)

app = FastAPI(
    title="SCA-EMPX API",
    description="Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas - STI S.A.S.",
    version="0.1.0",
)


@app.on_event("startup")
def startup():
    """Corrige esquema de registro_acceso en SQLite si la BD es antigua; añade columnas HU-03 a persona si faltan."""
    ensure_registro_acceso_schema()
    ensure_persona_visitante_columns()
    ensure_autorizacion_table()


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


@app.get("/registro-empleado")
def registro_empleado_page():
    """Página de registro de empleado con foto (HU-01)."""
    path = Path(__file__).parent / "static" / "registro-empleado.html"
    return FileResponse(path)


@app.get("/registro-visitante")
def registro_visitante_page():
    """Página de registro de visitante con foto (HU-03)."""
    path = Path(__file__).parent / "static" / "registro-visitante.html"
    return FileResponse(path)


@app.get("/autorizacion-visita")
def autorizacion_visita_page():
    """Pantalla para generar autorización de visita (HU-04)."""
    path = Path(__file__).parent / "static" / "autorizacion-visita.html"
    return FileResponse(path)


@app.get("/registrar-salida")
def registrar_salida_page():
    """Página para registrar salida por reconocimiento facial (HU-07)."""
    path = Path(__file__).parent / "static" / "registrar-salida.html"
    return FileResponse(path)


@app.get("/administracion-usuarios")
def administracion_usuarios_page():
    """Pantalla de administración de usuarios: login, listado, alta, activar/desactivar (HU-09)."""
    path = Path(__file__).parent / "static" / "administracion-usuarios.html"
    return FileResponse(path)


@app.get("/listado-personas")
def listado_personas_page():
    """Listado de personas con búsqueda y botón Desactivar/Activar (HU-02)."""
    path = Path(__file__).parent / "static" / "listado-personas.html"
    return FileResponse(path)
