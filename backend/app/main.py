"""Punto de entrada — SCA-EMPX API."""
import logging
import os
import threading
from pathlib import Path

# Silenciar logs de TensorFlow/DeepFace si están instalados (opcional en CI)
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"
try:
    logging.getLogger("tensorflow").setLevel(logging.ERROR)
    logging.getLogger("tf_keras").setLevel(logging.ERROR)
except Exception:
    pass

from fastapi import FastAPI  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.responses import HTMLResponse, JSONResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

from backend.app.api.v1 import api_router  # noqa: E402
from backend.app.api.v1.routes.ws import router as ws_router  # noqa: E402
from backend.app.db.database import init_db  # noqa: E402

try:
    from backend.app.ml.face_model import get_model  # noqa: E402
except ImportError:
    get_model = None  # CI sin dependencias ML (extra [ml])



# Directorios
ROOT        = Path(__file__).resolve().parents[2]
FRONTEND    = ROOT / "frontend" / "src"
STATIC_DIR  = FRONTEND / "static"
STATIC_DIR.mkdir(parents=True, exist_ok=True)

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
    """Pre-cargar modelo ML en background si está disponible."""
    init_db()
    if get_model is not None:
        threading.Thread(target=get_model, daemon=True).start()


# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(api_router, prefix="/api/v1")
app.include_router(ws_router,  prefix="/ws")

# ── Archivos estáticos (JS, CSS compartidos) ──────────────────────────────────
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


# ── Páginas HTML — rutas explícitas ──────────────────────────────────────────
def _page(name: str) -> HTMLResponse:
    return HTMLResponse((FRONTEND / name).read_text(encoding="utf-8"))


def _page_or_fallback(name: str, fallback_path: Path | None = None):
    """Devuelve la página HTML si existe; si no (ej. en contenedor sin frontend), None."""
    path = fallback_path or (FRONTEND / name)
    if path.exists():
        return HTMLResponse(path.read_text(encoding="utf-8"))
    return None


@app.get("/", include_in_schema=False)
def dashboard():
    """Retorna el dashboard principal (index.html) o info de API si no hay frontend."""
    response = _page_or_fallback("index.html")
    if response is not None:
        return response
    return JSONResponse(
        status_code=200,
        content={
            "service": "SCA-EMPX API",
            "docs": "/docs",
            "health": "/health",
            "message": "Use the frontend at port 80 or open /docs for the API.",
        },
    )

@app.get("/registro", include_in_schema=False)
def pg_registro():
    """Retorna la página de registro facial de personas."""
    return _page_or_fallback("registro.html") or JSONResponse(status_code=404, content={"detail": "Frontend not in this image; use port 80."})

@app.get("/acceso", include_in_schema=False)
def pg_acceso():
    """Retorna la página de control de acceso (entrada/salida)."""
    return _page_or_fallback("acceso.html") or JSONResponse(status_code=404, content={"detail": "Frontend not in this image; use port 80."})

@app.get("/visitante", include_in_schema=False)
def pg_visitante():
    """Retorna la página de registro de visitas externas."""
    return _page_or_fallback("visitante.html") or JSONResponse(status_code=404, content={"detail": "Frontend not in this image; use port 80."})

@app.get("/configuracion", include_in_schema=False)
def pg_config():
    """Retorna la página de configuración del sistema."""
    return _page_or_fallback("configuracion.html") or JSONResponse(status_code=404, content={"detail": "Frontend not in this image; use port 80."})

@app.get("/health", include_in_schema=False)
def health():
    """Endpoint de health-check para monitoreo de disponibilidad."""
    return {"status": "ok"}
