"""Punto de entrada — SCA-EMPX API."""
import logging
import os
import threading

# Silenciar logs de TensorFlow/DeepFace ANTES de importarlos
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
logging.getLogger("tensorflow").setLevel(logging.ERROR)
logging.getLogger("tf_keras").setLevel(logging.ERROR)

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402

from backend.app.api.v1 import api_router  # noqa: E402
from backend.app.api.v1.routes.ws import router as ws_router  # noqa: E402
from backend.app.db.database import init_db  # noqa: E402
from backend.app.ml.face_model import get_model  # noqa: E402


app = FastAPI(
    title="SCA-EMPX",
    description="Sistema de Control de Acceso Físico",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup():
    '''Pre-cargar modelo ML en background para que el primer request sea rápido'''
    init_db()
    threading.Thread(target=get_model, daemon=True).start()


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router,  prefix="/ws")


@app.get("/health", include_in_schema=False)
def health():
    """Endpoint de health-check para monitoreo de disponibilidad."""
    return {"status": "ok"}
