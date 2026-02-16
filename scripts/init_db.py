#!/usr/bin/env python3
"""
Inicializar base de datos SQLite: crear tablas y datos semilla (tipo_persona, usuario admin).
Ejecutar desde la raíz del proyecto: uv run python scripts/init_db.py
"""
import sys
from pathlib import Path

# Asegurar que el proyecto esté en el path
root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))

from backend.app.db.database import init_db, SessionLocal
from backend.app.db.models import Base, TipoPersona, UsuarioSistema
from backend.app.core.security import get_password_hash


def seed_tipos_persona(db):
    """Inserta tipos de persona si no existen."""
    if db.query(TipoPersona).first() is not None:
        print("  Tipos de persona ya existen, omitiendo.")
        return
    for nombre, desc in [
        ("visitante_temporal", "Visitante temporal"),
        ("empleado_propio", "Empleado propio de la empresa"),
        ("empleado_externo", "Empleado de empresa externa"),
    ]:
        db.add(TipoPersona(nombre_tipo=nombre, descripcion=desc, estado="activo"))
    db.commit()
    print("  Tipos de persona creados.")


def seed_admin(db):
    """Crea usuario admin por defecto si no existe (usuario: admin, contraseña: admin)."""
    if db.query(UsuarioSistema).filter(UsuarioSistema.nombre_usuario == "admin").first() is not None:
        print("  Usuario admin ya existe, omitiendo.")
        return
    db.add(UsuarioSistema(
        nombre_usuario="admin",
        hash_password=get_password_hash("admin"),
        rol="admin",
        estado="activo",
    ))
    db.commit()
    print("  Usuario admin creado (usuario: admin, contraseña: admin). Cambiar en producción.")


def main():
    print("Inicializando base de datos SQLite...")
    init_db()
    print("  Tablas creadas.")
    db = SessionLocal()
    try:
        seed_tipos_persona(db)
        seed_admin(db)
    finally:
        db.close()
    print("Listo.")


if __name__ == "__main__":
    main()
