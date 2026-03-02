"""Pruebas de los endpoints de catálogos — GET /api/v1/catalogos/*.

Rutas cubiertas:
    GET /api/v1/catalogos/areas
    GET /api/v1/catalogos/areas/{id}/cargos
    GET /api/v1/catalogos/cargos
    GET /api/v1/catalogos/tipos-persona

Los catálogos los siembra ``seed_test_db`` en conftest.py una sola vez.
Las pruebas son de solo lectura — no modifican datos.
"""
from __future__ import annotations



# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/catalogos/areas
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarAreas:
    """Pruebas del endpoint GET /api/v1/catalogos/areas."""

    def test_status_200(self, client):
        """Retorna HTTP 200."""
        r = client.get("/api/v1/catalogos/areas")
        assert r.status_code == 200

    def test_retorna_lista(self, client):
        """El cuerpo es una lista JSON."""
        r = client.get("/api/v1/catalogos/areas")
        assert isinstance(r.json(), list)

    def test_contiene_al_menos_3_areas(self, client):
        """Los catálogos sembrados incluyen al menos 3 áreas."""
        r = client.get("/api/v1/catalogos/areas")
        assert len(r.json()) >= 3

    def test_campos_requeridos(self, client):
        """Cada área tiene id_area y nombre."""
        r = client.get("/api/v1/catalogos/areas")
        for area in r.json():
            assert "id_area" in area
            assert "nombre" in area

    def test_areas_ordenadas_alfabeticamente(self, client):
        """Las áreas vienen en orden alfabético por nombre."""
        r      = client.get("/api/v1/catalogos/areas")
        nombres = [a["nombre"] for a in r.json()]
        assert nombres == sorted(nombres)

    def test_incluye_tecnologia(self, client):
        """El área 'Tecnología' está presente entre las sembradas."""
        r      = client.get("/api/v1/catalogos/areas")
        nombres = [a["nombre"] for a in r.json()]
        assert "Tecnología" in nombres

    def test_id_area_entero_positivo(self, client):
        """Los id_area son enteros positivos."""
        r = client.get("/api/v1/catalogos/areas")
        for area in r.json():
            assert isinstance(area["id_area"], int)
            assert area["id_area"] > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/catalogos/areas/{id}/cargos
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarCargosPorArea:
    """Pruebas del endpoint GET /api/v1/catalogos/areas/{id}/cargos."""

    def _get_area_id(self, client, nombre: str) -> int:
        r = client.get("/api/v1/catalogos/areas")
        areas = r.json()
        return next(a["id_area"] for a in areas if a["nombre"] == nombre)

    def test_status_200_area_valida(self, client):
        """Retorna 200 para un área existente."""
        area_id = self._get_area_id(client, "Tecnología")
        r = client.get(f"/api/v1/catalogos/areas/{area_id}/cargos")
        assert r.status_code == 200

    def test_retorna_lista(self, client):
        """El cuerpo es una lista."""
        area_id = self._get_area_id(client, "Tecnología")
        r = client.get(f"/api/v1/catalogos/areas/{area_id}/cargos")
        assert isinstance(r.json(), list)

    def test_cargos_tienen_campos(self, client):
        """Cada cargo tiene id_cargo, nombre, id_area."""
        area_id = self._get_area_id(client, "Tecnología")
        r = client.get(f"/api/v1/catalogos/areas/{area_id}/cargos")
        for cargo in r.json():
            assert "id_cargo" in cargo
            assert "nombre"   in cargo
            assert "id_area"  in cargo

    def test_todos_cargos_pertenecen_al_area(self, client):
        """Todos los cargos retornados tienen id_area == el área solicitada."""
        area_id = self._get_area_id(client, "Tecnología")
        r       = client.get(f"/api/v1/catalogos/areas/{area_id}/cargos")
        for cargo in r.json():
            assert cargo["id_area"] == area_id

    def test_area_sin_cargos_retorna_lista_vacia(self, client):
        """Un área sin cargos retorna lista vacía (9999 no existe)."""
        r = client.get("/api/v1/catalogos/areas/9999/cargos")
        assert r.status_code == 200
        assert r.json() == []

    def test_tecnologia_tiene_3_cargos(self, client):
        """El área Tecnología tiene exactamente 3 cargos sembrados."""
        area_id = self._get_area_id(client, "Tecnología")
        r = client.get(f"/api/v1/catalogos/areas/{area_id}/cargos")
        assert len(r.json()) == 3

    def test_cargos_ordenados_alfabeticamente(self, client):
        """Los cargos vienen ordenados por nombre."""
        area_id = self._get_area_id(client, "Tecnología")
        r       = client.get(f"/api/v1/catalogos/areas/{area_id}/cargos")
        nombres = [c["nombre"] for c in r.json()]
        assert nombres == sorted(nombres)


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/catalogos/cargos
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarTodosCargos:
    """Pruebas del endpoint GET /api/v1/catalogos/cargos."""

    def test_status_200(self, client):
        r = client.get("/api/v1/catalogos/cargos")
        assert r.status_code == 200

    def test_retorna_lista(self, client):
        r = client.get("/api/v1/catalogos/cargos")
        assert isinstance(r.json(), list)

    def test_contiene_9_cargos(self, client):
        """El seed siembra 9 cargos (3 por área × 3 áreas)."""
        r = client.get("/api/v1/catalogos/cargos")
        assert len(r.json()) >= 9

    def test_campos_requeridos(self, client):
        r = client.get("/api/v1/catalogos/cargos")
        for c in r.json():
            assert "id_cargo" in c
            assert "nombre"   in c
            assert "id_area"  in c

    def test_incluye_desarrollador_backend(self, client):
        r      = client.get("/api/v1/catalogos/cargos")
        nombres = [c["nombre"] for c in r.json()]
        assert "Desarrollador Backend" in nombres


# ═══════════════════════════════════════════════════════════════════════════════
#  GET /api/v1/catalogos/tipos-persona
# ═══════════════════════════════════════════════════════════════════════════════

class TestListarTiposPersona:
    """Pruebas del endpoint GET /api/v1/catalogos/tipos-persona."""

    def test_status_200(self, client):
        r = client.get("/api/v1/catalogos/tipos-persona")
        assert r.status_code == 200

    def test_retorna_lista(self, client):
        r = client.get("/api/v1/catalogos/tipos-persona")
        assert isinstance(r.json(), list)

    def test_contiene_3_tipos(self, client):
        """Los 3 tipos sembrados están presentes."""
        r = client.get("/api/v1/catalogos/tipos-persona")
        assert len(r.json()) >= 3

    def test_campos_requeridos(self, client):
        r = client.get("/api/v1/catalogos/tipos-persona")
        for t in r.json():
            assert "id_tipo_persona" in t
            assert "tipo"            in t
            assert "es_empleado"     in t

    def test_tipos_esperados(self, client):
        """Empleado, Visitante y Contratista existen."""
        r     = client.get("/api/v1/catalogos/tipos-persona")
        tipos = {t["tipo"] for t in r.json()}
        assert {"Empleado", "Visitante", "Contratista"}.issubset(tipos)

    def test_empleado_tiene_flag_true(self, client):
        """El tipo 'Empleado' tiene es_empleado=True."""
        r       = client.get("/api/v1/catalogos/tipos-persona")
        empleado = next(t for t in r.json() if t["tipo"] == "Empleado")
        assert empleado["es_empleado"] is True

    def test_visitante_tiene_flag_false(self, client):
        """El tipo 'Visitante' tiene es_empleado=False."""
        r        = client.get("/api/v1/catalogos/tipos-persona")
        visitante = next(t for t in r.json() if t["tipo"] == "Visitante")
        assert visitante["es_empleado"] is False

    def test_ordenados_alfabeticamente(self, client):
        r      = client.get("/api/v1/catalogos/tipos-persona")
        tipos  = [t["tipo"] for t in r.json()]
        assert tipos == sorted(tipos)
