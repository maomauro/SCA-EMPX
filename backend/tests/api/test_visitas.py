"""Pruebas de los endpoints de visitas — /api/v1/visitas/*.

Rutas cubiertas:
    POST   /api/v1/visitas/              → crear visita
    GET    /api/v1/visitas/              → listar visitas
    PATCH  /api/v1/visitas/{id}/salida   → registrar salida
"""
from __future__ import annotations



# ═══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def _get_tipo_id(client, tipo: str) -> int:
    r = client.get("/api/v1/catalogos/tipos-persona")
    return next(t["id_tipo_persona"] for t in r.json() if t["tipo"] == tipo)


def _get_cargo_id(client) -> int:
    r = client.get("/api/v1/catalogos/cargos")
    return r.json()[0]["id_cargo"]


def _crear_persona(client, nro: str, tipo: str = "Visitante", nombres: str = "Test") -> dict:
    body = {
        "tipo_documento":  "CC",
        "nro_documento":   nro,
        "nombres":         nombres,
        "id_tipo_persona": _get_tipo_id(client, tipo),
    }
    if tipo == "Empleado":
        body["id_cargo"] = _get_cargo_id(client)
    r = client.post("/api/v1/personas/", json=body)
    assert r.status_code == 200, r.text
    return r.json()


def _crear_visita(client, id_persona: int, motivo: str = "Reunión") -> dict:
    r = client.post("/api/v1/visitas/", json={"id_persona": id_persona, "motivo": motivo})
    assert r.status_code == 200, r.text
    return r.json()


# ═══════════════════════════════════════════════════════════════════════════════
#  POST /api/v1/visitas/  — Crear visita
# ═══════════════════════════════════════════════════════════════════════════════

class TestCrearVisita:
    """Pruebas del endpoint POST /api/v1/visitas/."""

    def test_crear_visita_visitante_ok(self, client):
        """Crear visita para un visitante retorna 200 con id_visita."""
        p = _crear_persona(client, nro="VIS_C001", tipo="Visitante")
        r = client.post("/api/v1/visitas/", json={
            "id_persona": p["id_persona"],
            "motivo": "Reunión de negocios",
        })
        assert r.status_code == 200
        data = r.json()
        assert data["id_visita"] > 0
        assert data["id_persona"] == p["id_persona"]

    def test_crear_visita_contratista_ok(self, client):
        """Crear visita para un contratista retorna 200."""
        p = _crear_persona(client, nro="VIS_C002", tipo="Contratista")
        r = client.post("/api/v1/visitas/", json={
            "id_persona": p["id_persona"],
            "motivo": "Mantenimiento equipos",
        })
        assert r.status_code == 200

    def test_persona_inexistente_404(self, client):
        """Crear visita con persona inexistente retorna 404."""
        r = client.post("/api/v1/visitas/", json={
            "id_persona": 99999,
            "motivo": "Visita fantasma",
        })
        assert r.status_code == 404

    def test_empleado_no_puede_tener_visita_400(self, client):
        """Intentar crear visita para un empleado retorna 400."""
        p = _crear_persona(client, nro="VIS_E001", tipo="Empleado")
        r = client.post("/api/v1/visitas/", json={
            "id_persona": p["id_persona"],
            "motivo": "No aplica para empleados",
        })
        assert r.status_code == 400

    def test_motivo_trimmed(self, client):
        """El motivo se guarda sin espacios al inicio/final."""
        p = _crear_persona(client, nro="VIS_M001")
        r = client.post("/api/v1/visitas/", json={
            "id_persona": p["id_persona"],
            "motivo": "  Visita técnica  ",
        })
        assert r.status_code == 200
        assert r.json()["motivo"] == "Visita técnica"

    def test_respuesta_incluye_nombres(self, client):
        """La respuesta incluye el nombre de la persona visitante."""
        p = _crear_persona(client, nro="VIS_NOM001", nombres="Carlos Ruiz")
        r = client.post("/api/v1/visitas/", json={
            "id_persona": p["id_persona"],
            "motivo": "Entrega de documentos",
        })
        assert r.json()["nombres"] == "Carlos Ruiz"

    def test_respuesta_incluye_fecha(self, client):
        """La respuesta incluye la fecha de la visita."""
        p = _crear_persona(client, nro="VIS_F001")
        r = client.post("/api/v1/visitas/", json={
            "id_persona": p["id_persona"],
            "motivo": "Auditoría",
        })
        assert r.json()["fecha"] is not None

    def test_crear_visita_genera_registro_acceso(self, client):
        """Crear una visita genera automáticamente un registro de acceso tipo 'entrada'."""
        p = _crear_persona(client, nro="VIS_REG001")
        _crear_visita(client, p["id_persona"])

        # Verificar que hay al menos 1 evento de acceso tipo 'entrada'
        r = client.get("/api/v1/events/?tipo=entrada")
        entradas = [e for e in r.json() if e["id_persona"] == p["id_persona"]]
        assert len(entradas) >= 1


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/visitas/  — Listar visitas
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarVisitas:
    """Pruebas del endpoint GET /api/v1/visitas/."""

    def test_lista_vacia_sin_visitas(self, client):
        """Sin visitas creadas retorna lista vacía."""
        r = client.get("/api/v1/visitas/")
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_visita_aparece_en_lista(self, client):
        """Una visita creada aparece en el listado."""
        p = _crear_persona(client, nro="VIS_L001")
        _crear_visita(client, p["id_persona"])
        r = client.get("/api/v1/visitas/")
        assert any(v["id_persona"] == p["id_persona"] for v in r.json())

    def test_filtro_por_persona(self, client):
        """El filtro ?id_persona retorna solo las visitas de esa persona."""
        p1 = _crear_persona(client, nro="VIS_FP001")
        p2 = _crear_persona(client, nro="VIS_FP002")
        _crear_visita(client, p1["id_persona"], motivo="Visita P1")
        _crear_visita(client, p2["id_persona"], motivo="Visita P2")

        r = client.get(f"/api/v1/visitas/?id_persona={p1['id_persona']}")
        assert r.status_code == 200
        for v in r.json():
            assert v["id_persona"] == p1["id_persona"]

    def test_campos_respuesta(self, client):
        """Cada visita incluye los campos requeridos."""
        p = _crear_persona(client, nro="VIS_CAM001")
        _crear_visita(client, p["id_persona"])
        r = client.get(f"/api/v1/visitas/?id_persona={p['id_persona']}")
        for v in r.json():
            assert "id_visita"    in v
            assert "id_persona"   in v
            assert "nombres"      in v
            assert "motivo"       in v
            assert "fecha"        in v
            assert "fecha_salida" in v

    def test_fecha_salida_nula_visita_activa(self, client):
        """Una visita recién creada tiene fecha_salida = null (activa)."""
        p = _crear_persona(client, nro="VIS_FS001")
        _crear_visita(client, p["id_persona"])
        r = client.get(f"/api/v1/visitas/?id_persona={p['id_persona']}")
        assert r.json()[0]["fecha_salida"] is None

    def test_max_100_visitas(self, client):
        """El endpoint retorna como máximo 100 visitas."""
        r = client.get("/api/v1/visitas/")
        assert len(r.json()) <= 100

    def test_ordenadas_por_fecha_desc(self, client):
        """Las visitas vienen ordenadas de la más reciente a la más antigua."""
        p = _crear_persona(client, nro="VIS_ORD001")
        _crear_visita(client, p["id_persona"], "Primera visita")
        _crear_visita(client, p["id_persona"], "Segunda visita")
        r  = client.get(f"/api/v1/visitas/?id_persona={p['id_persona']}")
        vs = r.json()
        if len(vs) >= 2:
            # fecha más reciente primero
            assert vs[0]["fecha"] >= vs[1]["fecha"]


# ═══════════════════════════════════════════════════════════════════════════════
#  PATCH /api/v1/visitas/{id}/salida  — Registrar salida
# ═══════════════════════════════════════════════════════════════════════════════

class TestRegistrarSalida:
    """Pruebas del endpoint PATCH /api/v1/visitas/{id}/salida."""

    def _read_visitas_route(self):
        """Lee la ruta correcta del endpoint de salida."""
        return "/api/v1"

    def test_registrar_salida_ok(self, client):
        """Registrar salida de una visita activa retorna 200 con fecha_salida."""
        p = _crear_persona(client, nro="SAL001")
        v = _crear_visita(client, p["id_persona"])
        r = client.patch(f"/api/v1/visitas/{v['id_visita']}/salida")
        assert r.status_code == 200
        assert r.json()["fecha_salida"] is not None

    def test_visita_inexistente_404(self, client):
        """Registrar salida de visita inexistente retorna 404."""
        r = client.patch("/api/v1/visitas/99999/salida")
        assert r.status_code == 404

    def test_salida_idempotente_segunda_vez(self, client):
        """Registrar salida dos veces retorna 200 en ambas (idempotente)."""
        p = _crear_persona(client, nro="SAL002")
        v = _crear_visita(client, p["id_persona"])
        r1 = client.patch(f"/api/v1/visitas/{v['id_visita']}/salida")
        r2 = client.patch(f"/api/v1/visitas/{v['id_visita']}/salida")
        assert r1.status_code == 200
        assert r2.status_code == 200

    def test_fecha_salida_es_timestamp(self, client):
        """La fecha_salida en la respuesta es un string ISO 8601."""
        p = _crear_persona(client, nro="SAL003")
        v = _crear_visita(client, p["id_persona"])
        r = client.patch(f"/api/v1/visitas/{v['id_visita']}/salida")
        data = r.json()
        assert isinstance(data["fecha_salida"], str)
        assert len(data["fecha_salida"]) > 10  # formato ISO

    def test_visita_cerrada_no_aparece_en_activas(self, client):
        """La visita con fecha_salida ya no es 'activa' (fecha_salida != null)."""
        p = _crear_persona(client, nro="SAL004")
        v = _crear_visita(client, p["id_persona"])
        client.patch(f"/api/v1/visitas/{v['id_visita']}/salida")

        r = client.get(f"/api/v1/visitas/?id_persona={p['id_persona']}")
        vis = next(x for x in r.json() if x["id_visita"] == v["id_visita"])
        assert vis["fecha_salida"] is not None
