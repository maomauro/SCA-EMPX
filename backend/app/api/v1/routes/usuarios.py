"""Rutas usuarios del sistema. HU-09."""
from fastapi import APIRouter

router = APIRouter()


@router.post("/login")
def login():
    return {"message": "Login (por implementar)"}


@router.get("/")
def listar_usuarios():
    return {"message": "Listado de usuarios (por implementar)"}


@router.post("/")
def crear_usuario():
    return {"message": "Crear usuario (por implementar)"}
