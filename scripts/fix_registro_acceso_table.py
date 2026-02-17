#!/usr/bin/env python3
"""
Recrea la tabla registro_acceso con el esquema actual (id_registro como INTEGER
autoincrement). Soluciona el error 500 al validar acceso si la BD se creó antes
del fix. No borra personas ni otros datos.
Ejecutar desde la raíz: uv run python scripts/fix_registro_acceso_table.py
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from backend.app.db.database import engine
from backend.app.db.models import Base, RegistroAcceso


def main():
    # Cargar todos los modelos para que las FKs existan
    import backend.app.db.models  # noqa: F401
    RegistroAcceso.__table__.drop(engine, checkfirst=True)
    RegistroAcceso.__table__.create(engine)
    print("Tabla registro_acceso recreada correctamente. Vuelve a probar validar acceso.")


if __name__ == "__main__":
    main()
