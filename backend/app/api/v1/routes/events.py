"""Rutas eventos entrada/salida. HU-06, HU-07."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def listar_eventos():
    return {"message": "Listado de eventos (por implementar)"}


@router.post("/exit")
def registrar_salida():
    return {"message": "Registro de salida (por implementar)"}
