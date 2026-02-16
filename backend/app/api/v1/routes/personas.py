"""Rutas personas (empleados y visitantes). HU-01, HU-02, HU-03, HU-10."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def listar_personas():
    return {"message": "Listado de personas (por implementar)"}


@router.post("/")
def registrar_persona():
    return {"message": "Registro de persona (por implementar)"}


@router.patch("/{persona_id:int}")
def actualizar_persona(persona_id: int):
    return {"message": f"Actualizar persona {persona_id} (por implementar)"}
