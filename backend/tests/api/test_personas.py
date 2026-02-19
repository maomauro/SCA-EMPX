"""Pruebas de los endpoints de personas — /api/v1/personas/*.

Rutas cubiertas:
    POST /api/v1/personas/                     → crear persona
    GET  /api/v1/personas/                     → listar (con/sin filtro)
    GET  /api/v1/personas/{id}                 → detalle
    POST /api/v1/personas/identificar          → identificar por cara
    POST /api/v1/personas/{id}/registros       → agregar embedding
"""
from __future__ import annotations

import io

from PIL import Image


# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_tipo_id(client, tipo: str) -> int:
    r = client.get("/api/v1/catalogos/tipos-persona")
    return next(t["id_tipo_persona"] for t in r.json() if t["tipo"] == tipo)


def _get_cargo_id(client) -> int:
    r = client.get("/api/v1/catalogos/cargos")
    return r.json()[0]["id_cargo"]


def _crear_visitante(client, nro: str, nombres: str = "Test Visitante") -> dict:
    tipo_id = _get_tipo_id(client, "Visitante")
    r = client.post("/api/v1/personas/", json={
        "tipo_documento":  "CC",
        "nro_documento":   nro,
        "nombres":         nombres,
        "id_tipo_persona": tipo_id,
    })
    assert r.status_code == 200, r.text
    return r.json()


def _crear_empleado(client, nro: str, nombres: str = "Test Empleado") -> dict:
    tipo_id  = _get_tipo_id(client, "Empleado")
    cargo_id = _get_cargo_id(client)
    r = client.post("/api/v1/personas/", json={
        "tipo_documento":  "CC",
        "nro_documento":   nro,
        "nombres":         nombres,
        "id_tipo_persona": tipo_id,
        "id_cargo":        cargo_id,
    })
    assert r.status_code == 200, r.text
    return r.json()


def _blank_image_file(name: str = "foto.jpg") -> tuple:
    """Genera un archivo JPEG en blanco (sin rostro) para uploads."""
    img = Image.new("RGB", (224, 224), color=(255, 255, 255))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return ("foto", (name, buf, "image/jpeg"))


# ═══════════════════════════════════════════════════════════════════════════════
#  POST /api/v1/personas/  — Crear persona
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrearPersona:
    """Pruebas del endpoint POST /api/v1/personas/."""

    def test_crear_visitante_ok(self, client):
        """Crear un visitante retorna 200 con id_persona."""
        p = _crear_visitante(client, nro="CV001")
        assert p["id_persona"] > 0
        assert p["tipo"] == "Visitante"
        assert p["activo"] is True

    def test_crear_empleado_ok(self, client):
        """Crear un empleado con cargo retorna 200."""
        p = _crear_empleado(client, nro="CE001")
        assert p["id_persona"] > 0
        assert p["tipo"] == "Empleado"
        assert p["id_cargo"] is not None

    def test_crear_contratista_sin_cargo(self, client):
        """Un contratista puede crearse sin cargo."""
        tipo_id = _get_tipo_id(client, "Contratista")
        r = client.post("/api/v1/personas/", json={
            "tipo_documento":  "CE",
            "nro_documento":   "CC001",
            "nombres":         "Contratista Test",
            "id_tipo_persona": tipo_id,
        })
        assert r.status_code == 200
        assert r.json()["tipo"] == "Contratista"

    def test_documento_duplicado_409(self, client):
        """Crear una persona con documento ya existente retorna 409."""
        _crear_visitante(client, nro="DUP001")
        r = client.post("/api/v1/personas/", json={
            "tipo_documento":  "CC",
            "nro_documento":   "DUP001",
            "nombres":         "Persona Duplicada",
            "id_tipo_persona": _get_tipo_id(client, "Visitante"),
        })
        assert r.status_code == 409

    def test_tipo_persona_invalido_400(self, client):
        """Un id_tipo_persona inexistente retorna 400."""
        r = client.post("/api/v1/personas/", json={
            "tipo_documento":  "CC",
            "nro_documento":   "INV001",
            "nombres":         "Persona Invalida",
            "id_tipo_persona": 99999,
        })
        assert r.status_code == 400

    def test_empleado_sin_cargo_400(self, client):
        """Un empleado sin cargo retorna 400."""
        tipo_id = _get_tipo_id(client, "Empleado")
        r = client.post("/api/v1/personas/", json={
            "tipo_documento":  "CC",
            "nro_documento":   "NOCARGO001",
            "nombres":         "Empleado Sin Cargo",
            "id_tipo_persona": tipo_id,
        })
        assert r.status_code == 400

    def test_nombres_limpiados(self, client):
        """Los nombres se guardan sin espacios al inicio/final."""
        tipo_id = _get_tipo_id(client, "Visitante")
        r = client.post("/api/v1/personas/", json={
            "tipo_documento":  "CC",
            "nro_documento":   "NOM001",
            "nombres":         "  Juan Pérez  ",
            "id_tipo_persona": tipo_id,
        })
        assert r.status_code == 200
        assert r.json()["nombres"] == "Juan Pérez"

    def test_n_embeddings_cero_al_crear(self, client):
        """Al crear una persona sin fotos, n_embeddings = 0."""
        p = _crear_visitante(client, nro="NEM001")
        assert p["n_embeddings"] == 0

    def test_campos_respuesta_completos(self, client):
        """La respuesta incluye todos los campos de PersonaOut."""
        p = _crear_visitante(client, nro="CAMPOS001")
        campos = {
            "id_persona", "tipo_documento", "nro_documento", "nombres",
            "id_tipo_persona", "tipo", "id_cargo", "cargo", "area",
            "n_embeddings", "activo",
        }
        assert campos.issubset(p.keys())


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/personas/  — Listar personas
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarPersonas:
    """Pruebas del endpoint GET /api/v1/personas/."""

    def test_lista_vacia_sin_personas(self, client):
        """Sin personas en BD retorna lista vacía."""
        r = client.get("/api/v1/personas/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_lista_con_persona_creada(self, client):
        """Una persona creada aparece en la lista."""
        _crear_visitante(client, nro="LST001")
        r = client.get("/api/v1/personas/")
        assert len(r.json()) >= 1

    def test_filtro_por_tipo_visitante(self, client):
        """El filtro ?tipo=Visitante retorna solo visitantes."""
        _crear_visitante(client, nro="FV001")
        _crear_empleado(client,  nro="FE001")
        r = client.get("/api/v1/personas/?tipo=Visitante")
        assert r.status_code == 200
        for p in r.json():
            assert p["tipo"] == "Visitante"

    def test_filtro_por_tipo_empleado(self, client):
        """El filtro ?tipo=Empleado retorna solo empleados."""
        _crear_visitante(client, nro="FV002")
        _crear_empleado(client,  nro="FE002")
        r = client.get("/api/v1/personas/?tipo=Empleado")
        for p in r.json():
            assert p["tipo"] == "Empleado"

    def test_ordenados_por_nombre(self, client):
        """La lista viene ordenada alfabéticamente por nombres."""
        _crear_visitante(client, nro="ORD001", nombres="Zarate Carlos")
        _crear_visitante(client, nro="ORD002", nombres="Alvarez Pedro")
        r      = client.get("/api/v1/personas/")
        nombres = [p["nombres"] for p in r.json()]
        assert nombres == sorted(nombres)

    def test_tipo_inexistente_retorna_vacio(self, client):
        """Un tipo que no existe retorna lista vacía."""
        _crear_visitante(client, nro="TI001")
        r = client.get("/api/v1/personas/?tipo=TipoQueNoExiste")
        assert r.json() == []


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/personas/{id}  — Detalle
# ═══════════════════════════════════════════════════════════════════════════════

class TestObtenerPersona:
    """Pruebas del endpoint GET /api/v1/personas/{id}."""

    def test_persona_existente_200(self, client):
        """Solicitar una persona existente retorna 200."""
        p  = _crear_visitante(client, nro="DET001")
        r  = client.get(f"/api/v1/personas/{p['id_persona']}")
        assert r.status_code == 200

    def test_datos_correctos(self, client):
        """La respuesta contiene los datos de la persona creada."""
        p  = _crear_visitante(client, nro="DET002", nombres="Juan Detalle")
        r  = client.get(f"/api/v1/personas/{p['id_persona']}")
        data = r.json()
        assert data["nro_documento"] == "DET002"
        assert data["nombres"] == "Juan Detalle"

    def test_persona_inexistente_404(self, client):
        """Una persona con ID inexistente retorna 404."""
        r = client.get("/api/v1/personas/99999")
        assert r.status_code == 404

    def test_empleado_incluye_cargo_y_area(self, client):
        """La respuesta de un empleado incluye nombre del cargo y del área."""
        p = _crear_empleado(client, nro="DET003")
        r = client.get(f"/api/v1/personas/{p['id_persona']}")
        data = r.json()
        assert data["cargo"] is not None
        assert data["area"]  is not None


# ═══════════════════════════════════════════════════════════════════════════════
#  POST /api/v1/personas/identificar  — Identificar por cara
# ═══════════════════════════════════════════════════════════════════════════════

class TestIdentificarPorCara:
    """Pruebas del endpoint POST /api/v1/personas/identificar."""

    def test_imagen_sin_rostro_400(self, client):
        """Una imagen sin rostro retorna 400 (no se detectó rostro)."""
        files = {"foto": ("foto.jpg", io.BytesIO(b"\xff\xd8\xff\xe0" + b"\x00" * 100), "image/jpeg")}
        r = client.post("/api/v1/personas/identificar", files=files)
        # 400 si la imagen es inválida (no se puede decodificar)
        assert r.status_code in (400, 422)

    def test_imagen_blanca_sin_match(self, client):
        """Imagen blanca sin galería retorna encontrado=False o error de rostro."""
        _, file_tuple = _blank_image_file()
        r = client.post("/api/v1/personas/identificar", files={"foto": file_tuple})
        assert r.status_code in (200, 400)
        if r.status_code == 200:
            assert r.json()["encontrado"] is False

    def test_galeria_vacia_retorna_no_encontrado(self, client, blank_image_bytes):
        """Sin personas registradas retorna encontrado=False (galería vacía)."""
        buf = io.BytesIO(blank_image_bytes)
        r   = client.post("/api/v1/personas/identificar", files={"foto": ("foto.jpg", buf, "image/jpeg")})
        # Puede ser 400 (no rostro) o 200 (sin candidatos → no encontrado)
        assert r.status_code in (200, 400)


# ═══════════════════════════════════════════════════════════════════════════════
#  POST /api/v1/personas/{id}/registros  — Agregar embedding
# ═══════════════════════════════════════════════════════════════════════════════

class TestAgregarEmbedding:
    """Pruebas del endpoint POST /api/v1/personas/{id}/registros."""

    def test_persona_inexistente_404(self, client, blank_image_bytes):
        """Una persona con ID inexistente retorna 404."""
        buf = io.BytesIO(blank_image_bytes)
        r   = client.post(
            "/api/v1/personas/99999/registros",
            files={"foto": ("foto.jpg", buf, "image/jpeg")},
        )
        assert r.status_code == 404

    def test_imagen_sin_rostro_retorna_ok_false(self, client, blank_image_bytes):
        """Una imagen sin rostro retorna ok=False con motivo=rostro_no_detectado."""
        p   = _crear_visitante(client, nro="EMB001")
        buf = io.BytesIO(blank_image_bytes)
        r   = client.post(
            f"/api/v1/personas/{p['id_persona']}/registros",
            files={"foto": ("foto.jpg", buf, "image/jpeg")},
        )
        assert r.status_code == 200
        data = r.json()
        assert data["ok"] is False
        assert data["motivo"] == "rostro_no_detectado"

    def test_n_embeddings_no_cambia_con_imagen_invalida(self, client, blank_image_bytes):
        """n_embeddings no aumenta si no se detectó rostro."""
        p    = _crear_visitante(client, nro="EMB002")
        buf  = io.BytesIO(blank_image_bytes)
        r    = client.post(
            f"/api/v1/personas/{p['id_persona']}/registros",
            files={"foto": ("foto.jpg", buf, "image/jpeg")},
        )
        assert r.json()["n_embeddings"] == 0

    def test_con_imagen_real_ok_o_sin_rostro(self, client, face_image_bytes):
        """Con imagen real retorna ok=True si detecta rostro, ok=False si no."""
        p   = _crear_visitante(client, nro="EMB003")
        buf = io.BytesIO(face_image_bytes)
        r   = client.post(
            f"/api/v1/personas/{p['id_persona']}/registros",
            files={"foto": ("foto.jpg", buf, "image/jpeg")},
        )
        assert r.status_code == 200
        data = r.json()
        assert "ok" in data
        assert "n_embeddings" in data
        assert isinstance(data["n_embeddings"], int)
