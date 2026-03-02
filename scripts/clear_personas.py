#!/usr/bin/env python3
"""
Borra todos los datos de personas (empleados/visitantes) y sus registros relacionados.
Mantiene tipos de persona y usuario admin. Útil para volver a probar el registro.
Ejecutar desde la raíz: uv run python scripts/clear_personas.py
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from backend.app.db.database import SessionLocal
from backend.app.db.models import Persona, ReconocimientoFacial, RegistroAcceso, UsuarioSistema


def main():
    db = SessionLocal()
    try:
        # Orden por FKs: registro_acceso -> reconocimiento_facial -> persona; usuario_sistema.id_persona opcional
        deleted_access = db.query(RegistroAcceso).delete()
        deleted_reco = db.query(ReconocimientoFacial).delete()
        db.query(UsuarioSistema).filter(UsuarioSistema.id_persona.isnot(None)).update(
            {UsuarioSistema.id_persona: None}, synchronize_session=False
        )
        deleted_personas = db.query(Persona).delete()
        db.commit()
        print("Datos borrados:")
        print("  Registros de acceso:", deleted_access)
        print("  Reconocimiento facial:", deleted_reco)
        print("  Personas:", deleted_personas)
        print("Listo. Puedes registrar empleados de nuevo.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
