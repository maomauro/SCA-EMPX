from fastapi import APIRouter
from backend.app.api.v1.routes import catalogos, personas, acceso, visitas, config, events

api_router = APIRouter()
api_router.include_router(catalogos.router, prefix="/catalogos", tags=["catalogos"])
api_router.include_router(personas.router,  prefix="/personas",  tags=["personas"])
api_router.include_router(acceso.router,    prefix="/acceso",    tags=["acceso"])
api_router.include_router(visitas.router,   prefix="/visitas",   tags=["visitas"])
api_router.include_router(config.router,    prefix="/config",    tags=["config"])
api_router.include_router(events.router,    prefix="/events",    tags=["events"])
