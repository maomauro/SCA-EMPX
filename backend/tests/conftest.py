"""Fixtures compartidas para todos los tests del backend SCA-EMPX.

Jerarquía de fixtures
---------------------
engine_test (session)
  └── seed_test_db (session, autouse) → TipoPersona / Area / Cargo
        └── db_session (function)     → sesión limpia por test
              └── client (function)   → TestClient con BD de test

face_image_bytes (session) → descarga/genera imagen de rostro real
"""
from __future__ import annotations

import io
import os
import urllib.request

# Silenciar TF antes de cualquier import de la app
os.environ["TF_CPP_MIN_LOG_LEVEL"]  = "3"
os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

import numpy as np
import pytest
from PIL import Image, ImageDraw
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from backend.app.db.models import (
    Base, Area, Cargo, TipoPersona,
    Persona, Registro, Visita,
)
from backend.app.db.database import get_db


# ── URL de imagen de rostro pública (Wikipedia Commons, CC-BY-SA) ─────────────
_FACE_URL = (
    "https://upload.wikimedia.org/wikipedia/commons/thumb/"
    "4/43/Face_of_a_girl_%28Mongolian%2C_female_face%29.jpg/"
    "157px-Face_of_a_girl_%28Mongolian%2C_female_face%29.jpg"
)
_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
_FACE_PATH  = os.path.join(_ASSETS_DIR, "face.jpg")

# ── Motor de test — SQLite en memoria, una sola conexión compartida ───────────
# StaticPool garantiza que todas las sesiones (incluidas las de TestClient)
# comparten el mismo objeto de conexión, por lo que ven la misma BD en memoria.
_TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
_TestSession = sessionmaker(autocommit=False, autoflush=False, bind=_TEST_ENGINE)


# ═══════════════════════════════════════════════════════════════════════════════
#  FIXTURES DE BASE DE DATOS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def engine_test():
    """Motor SQLite en memoria para toda la sesión de prueba.

    Crea todas las tablas al inicio y las elimina al final.
    """
    Base.metadata.create_all(bind=_TEST_ENGINE)
    yield _TEST_ENGINE
    Base.metadata.drop_all(bind=_TEST_ENGINE)


@pytest.fixture(scope="session", autouse=True)
def seed_test_db(engine_test):
    """Siembra catálogos base (TipoPersona, Area, Cargo) una vez por sesión.

    Estos registros no se limpian entre tests ya que son datos de referencia
    inmutables que todos los tests necesitan.
    """
    db = _TestSession()
    try:
        if db.query(TipoPersona).first() is None:
            db.add_all([
                TipoPersona(tipo="Empleado",    descripcion="Empleado directo",          es_empleado=True),
                TipoPersona(tipo="Visitante",   descripcion="Visitante externo",         es_empleado=False),
                TipoPersona(tipo="Contratista", descripcion="Personal de contratista",   es_empleado=False),
            ])
            db.flush()

        if db.query(Area).first() is None:
            a1 = Area(nombre="Tecnología")
            a2 = Area(nombre="Operaciones")
            a3 = Area(nombre="Recursos Humanos")
            db.add_all([a1, a2, a3])
            db.flush()
            db.add_all([
                Cargo(nombre="Desarrollador Backend",  id_area=a1.id_area),
                Cargo(nombre="Desarrollador Frontend", id_area=a1.id_area),
                Cargo(nombre="Analista de Datos",      id_area=a1.id_area),
                Cargo(nombre="Supervisor",             id_area=a2.id_area),
                Cargo(nombre="Operario",               id_area=a2.id_area),
                Cargo(nombre="Jefe de Planta",         id_area=a2.id_area),
                Cargo(nombre="Coordinador RRHH",       id_area=a3.id_area),
                Cargo(nombre="Psicólogo",              id_area=a3.id_area),
                Cargo(nombre="Auxiliar RRHH",          id_area=a3.id_area),
            ])
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture()
def db_session(engine_test):
    """Sesión de BD con limpieza automática de datos transaccionales al finalizar.

    Garantiza que cada test parte de una BD con solo los catálogos base, sin
    personas, registros ni visitas residuales de tests previos.
    """
    db = _TestSession()
    yield db
    # Limpieza ordenada respetando FK
    db.query(Registro).delete()
    db.query(Visita).delete()
    db.query(Persona).delete()
    db.commit()
    db.close()


def _override_get_db():
    """Dependencia FastAPI que inyecta la BD de test."""
    db = _TestSession()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture()
def client():
    """TestClient de FastAPI con la BD de test inyectada via override.

    Limpia los datos transaccionales después de cada test para garantizar
    aislamiento entre pruebas de API.
    """
    from backend.app.main import app  # import tardío para que env vars ya estén

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app, raise_server_exceptions=False) as c:
        yield c
    app.dependency_overrides.clear()

    # Limpieza post-test
    db = _TestSession()
    db.query(Registro).delete()
    db.query(Visita).delete()
    db.query(Persona).delete()
    db.commit()
    db.close()


# ═══════════════════════════════════════════════════════════════════════════════
#  FIXTURES DE CATÁLOGOS (helpers para tests de API)
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture()
def tipo_visitante(db_session) -> TipoPersona:
    """Retorna el TipoPersona 'Visitante' de la BD de test."""
    return db_session.query(TipoPersona).filter_by(tipo="Visitante").first()


@pytest.fixture()
def tipo_empleado(db_session) -> TipoPersona:
    """Retorna el TipoPersona 'Empleado' de la BD de test."""
    return db_session.query(TipoPersona).filter_by(tipo="Empleado").first()


@pytest.fixture()
def cargo_dev(db_session) -> Cargo:
    """Retorna el Cargo 'Desarrollador Backend' de la BD de test."""
    return db_session.query(Cargo).filter_by(nombre="Desarrollador Backend").first()


# ═══════════════════════════════════════════════════════════════════════════════
#  FIXTURES DE IMAGEN FACIAL
# ═══════════════════════════════════════════════════════════════════════════════

def _synthetic_face_bytes() -> bytes:
    """Genera una imagen sintética con forma ovalada similar a un rostro.

    No pasa los detectores YOLO/MTCNN, pero sirve para probar que el pipeline
    rechaza correctamente imágenes sin rostro.
    """
    img = Image.new("RGB", (224, 224), color=(210, 180, 140))
    draw = ImageDraw.Draw(img)
    # Forma ovalada (cara)
    draw.ellipse([50, 30, 174, 180], fill=(240, 200, 160), outline=(180, 140, 100), width=2)
    # Ojos
    draw.ellipse([80, 80, 100, 100], fill=(60, 40, 20))
    draw.ellipse([124, 80, 144, 100], fill=(60, 40, 20))
    # Nariz
    draw.polygon([(112, 105), (107, 130), (117, 130)], fill=(200, 160, 120))
    # Boca
    draw.arc([95, 135, 129, 155], start=0, end=180, fill=(160, 80, 80), width=2)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def _download_face_bytes() -> bytes | None:
    """Intenta descargar la imagen de rostro desde Wikipedia Commons.

    Returns:
        Bytes JPEG si la descarga fue exitosa, ``None`` en caso contrario.
    """
    try:
        req = urllib.request.Request(
            _FACE_URL,
            headers={"User-Agent": "SCA-EMPX-Tests/1.0"},
        )
        with urllib.request.urlopen(req, timeout=15) as resp:  # noqa: S310
            data = resp.read()
        # Verificar que sea una imagen JPEG/PNG válida
        Image.open(io.BytesIO(data)).verify()
        return data
    except Exception:
        return None


@pytest.fixture(scope="session")
def face_image_bytes() -> bytes:
    """Retorna bytes JPEG de un rostro real para pruebas del modelo ML.

    Estrategia (en orden de prioridad):
        1. Usa ``backend/tests/assets/face.jpg`` si existe.
        2. Descarga la imagen desde Wikipedia Commons y la guarda en caché.
        3. Genera una imagen sintética (no supera detección de rostros).

    Note:
        Para pruebas de detección real coloca tu propia imagen en
        ``backend/tests/assets/face.jpg`` (ver ``assets/README.md``).
    """
    # 1. Imagen local en caché
    if os.path.exists(_FACE_PATH):
        with open(_FACE_PATH, "rb") as f:
            return f.read()

    # 2. Descargar y guardar en caché
    os.makedirs(_ASSETS_DIR, exist_ok=True)
    data = _download_face_bytes()
    if data:
        with open(_FACE_PATH, "wb") as f:
            f.write(data)
        return data

    # 3. Imagen sintética (fallback — no detecta rostro)
    return _synthetic_face_bytes()


@pytest.fixture(scope="session")
def blank_image_bytes() -> bytes:
    """Retorna bytes JPEG de una imagen en blanco (sin rostro)."""
    img = Image.new("RGB", (224, 224), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


# ═══════════════════════════════════════════════════════════════════════════════
#  FIXTURES DE EMBEDDINGS SINTÉTICOS
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def emb_a() -> np.ndarray:
    """Embedding normalizado sintético A — vector uniforme."""
    rng = np.random.default_rng(seed=42)
    v = rng.random(512).astype(np.float32)
    return v / np.linalg.norm(v)


@pytest.fixture(scope="session")
def emb_b() -> np.ndarray:
    """Embedding normalizado sintético B — ligeramente diferente de A."""
    rng = np.random.default_rng(seed=99)
    v = rng.random(512).astype(np.float32)
    return v / np.linalg.norm(v)
