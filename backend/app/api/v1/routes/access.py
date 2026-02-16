"""Rutas validación de acceso. HU-05."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/validate")
def validar_acceso():
    return {"message": "Validación de acceso facial (por implementar)"}
