from fastapi import APIRouter

from backend.app.api.v1.routes import personas, access, events, autorizaciones, usuarios

api_router = APIRouter()
api_router.include_router(personas.router, prefix="/personas", tags=["personas"])
api_router.include_router(access.router, prefix="/access", tags=["access"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(autorizaciones.router, prefix="/autorizaciones", tags=["autorizaciones"])
api_router.include_router(usuarios.router, prefix="/usuarios", tags=["usuarios"])
