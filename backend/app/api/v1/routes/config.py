"""
Endpoint de configuración del sistema.

Agrupa operaciones administrativas que afectan el estado global de la
aplicación. Actualmente expone el restablecimiento de la base de datos
a su estado de fábrica, útil en entornos de desarrollo y pruebas.

Rutas:
    POST /config/reset-db  → Elimina personas, registros y visitas.
"""
from fastapi import APIRouter
from backend.app.db.database import reset_db

router = APIRouter()


@router.post("/reset-db")
def reset_base_de_datos():
    """Restablece la base de datos a su estado de fábrica.

    Elimina todos los registros de ``personas``, ``registros`` y ``visitas``.
    Las tablas de catálogo (``areas``, ``cargos``, ``tipos_persona``) se
    conservan intactas.

    Returns:
        ``{"ok": True, "mensaje": "..."}`` confirmando el restablecimiento.

    Warning:
        Operación irreversible. No usar en producción sin respaldo previo.
    """
    reset_db()
    return {"ok": True, "mensaje": "Base de datos restablecida a estado de fábrica."}
