"""Rutas autorizaciones de visita. HU-04."""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def listar_autorizaciones():
    return {"message": "Listado de autorizaciones (por implementar)"}


@router.post("/")
def crear_autorizacion():
    return {"message": "Crear autorización (por implementar)"}
