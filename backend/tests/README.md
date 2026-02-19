# Tests — SCA-EMPX Backend

Registro completo de la suite de pruebas del backend. Las pruebas **no usan mocks**; cargan los modelos de ML reales (HuggingFace y DeepFace Facenet512).

---

## Estructura

```
backend/tests/
├── conftest.py              ← Fixtures compartidas (BD, client, imágenes, embeddings)
├── assets/
│   ├── README.md            ← Instrucciones para agregar imágenes de prueba
│   └── face.jpg             ← Imagen de rostro real (agregar manualmente, ver assets/README.md)
├── unit/
│   ├── test_models.py       ← ORM: creación, relaciones, restricciones, cascade
│   ├── test_database.py     ← init_db, _seed, reset_db, get_db
│   └── test_face_utils.py   ← Funciones matemáticas puras: cosine_similarity,
│                               embedding_to_bytes, bytes_to_embedding, find_best_match
├── ml/
│   ├── test_hf_model.py     ← Modelo HuggingFace (Wide-ResNet-101-2 + ArcFace + YOLO)
│   ├── test_fallback_model.py ← Modelo fallback DeepFace Facenet512 + MTCNN
│   └── test_pipeline.py     ← Funciones públicas del pipeline: get_model,
│                               get_embedding_from_bytes, serialización completa
└── api/
    ├── test_catalogos.py    ← GET /api/v1/catalogos/* (áreas, cargos, tipos)
    ├── test_personas.py     ← POST/GET /api/v1/personas/* (CRUD + identificar)
    ├── test_visitas.py      ← POST/GET/PATCH /api/v1/visitas/*
    ├── test_events.py       ← GET /api/v1/events/ y /events/hoy
    └── test_acceso.py       ← POST /api/v1/acceso/validar (pipeline completo)
```

---

## Requisitos previos

```powershell
# Instalar dependencias de desarrollo (ya incluidas en pyproject.toml)
uv sync

# Verificar instalación
uv run pytest --version
```

### Dependencias de test

| Paquete    | Uso                                  |
|------------|--------------------------------------|
| `pytest`   | Framework de pruebas                 |
| `httpx`    | TestClient de FastAPI                |
| `Pillow`   | Generación/manipulación de imágenes  |
| `numpy`    | Operaciones con embeddings           |

---

## Ejecución

### Ruta rápida — solo unit tests (sin modelos ML)

```powershell
uv run pytest backend/tests/unit/ -v
```

Tiempo estimado: **< 10 segundos**.  
No requiere red ni descarga de modelos.

---

### Suite completa (incluye ML)

```powershell
uv run pytest backend/tests/ -v -m "not slow"
```

> **Nota:** Los tests de ML están marcados con `@pytest.mark.slow`.  
> Omitir `-m "not slow"` para ejecutarlos todos.

```powershell
# Incluir tests lentos (carga de modelos HF + DeepFace)
uv run pytest backend/tests/ -v
```

Tiempo estimado primer run: **5–15 minutos** (descarga de modelos).  
Runs posteriores (modelos en caché): **2–5 minutos**.

---

### Por módulo

```powershell
# Solo unit
uv run pytest backend/tests/unit/ -v

# Solo ML
uv run pytest backend/tests/ml/ -v

# Solo API
uv run pytest backend/tests/api/ -v

# Un archivo específico
uv run pytest backend/tests/api/test_catalogos.py -v

# Una clase específica
uv run pytest backend/tests/api/test_personas.py::TestCrearPersona -v

# Un test específico
uv run pytest backend/tests/unit/test_face_utils.py::TestCosineSimilarity::test_mismo_vector_similitud_1 -v
```

---

### Filtrar por marcador

```powershell
# Solo tests lentos (modelos ML)
uv run pytest backend/tests/ -m slow -v

# Excluir tests lentos
uv run pytest backend/tests/ -m "not slow" -v
```

---

### Con cobertura

```powershell
uv run pytest backend/tests/ --cov=backend/app --cov-report=html -m "not slow"
# El reporte HTML se genera en htmlcov/index.html
```

---

## Base de datos de test

Las pruebas usan **SQLite en memoria** (`sqlite:///:memory:`), completamente aislado de `backend/app/db/sca.db`.

- Los catálogos base (TipoPersona, Area, Cargo) se cargan **una vez** al inicio de la sesión de pytest.
- Cada test recibe una sesión limpia: los datos transaccionales (Persona, Registro, Visita) se eliminan después de cada test.
- **No se modifica ni crea ningún archivo `.db` en producción** durante los tests.

---

## Imagen de rostro para tests ML

Los tests que prueban el pipeline completo (detección + embedding) requieren una imagen real con un rostro humano bien iluminado y centrado.

**Estrategia automática:**

1. Si existe `backend/tests/assets/face.jpg` → se usa directamente.
2. Si no existe → intenta descargarse desde Wikipedia Commons.
3. Si la descarga falla → se genera una imagen sintética (no supera la detección facial; los tests de pipeline se saltan con `pytest.skip`).

**Para máxima cobertura ML**, coloca tu propia imagen en:

```
backend/tests/assets/face.jpg
```

Ver instrucciones detalladas en [assets/README.md](assets/README.md).

---

## Convenciones de código

| Convención | Descripción |
|---|---|
| Clases de test | `class TestNombreFeature:` |
| Nombre de tests | `def test_descripcion_comportamiento_esperado(self, ...)` |
| Fixtures de BD  | `db_session` — función-scoped, limpia después de cada test |
| Fixtures de API | `client` — función-scoped, TestClient con BD de test |
| Fixtures lentas | `hf_model`, `fallback_model` — session-scoped, un solo load |
| Saltar sin datos | `pytest.skip(...)` cuando la imagen no tiene rostro |
| Sin mocks | Toda la lógica usa las implementaciones reales |

---

## Resumen de cobertura objetivo

| Módulo | Tests | Cobertura objetivo |
|---|---|---|
| `db/models.py` | 23 tests | 100% |
| `db/database.py` | 14 tests | ~90% |
| `ml/face_model.py` (math) | 22 tests | 100% funciones puras |
| `ml/face_model.py` (HF) | 11 tests | ~80% (depende de rostro) |
| `ml/face_model.py` (fallback) | 10 tests | ~80% (depende de rostro) |
| `ml/face_model.py` (pipeline) | 9 tests | ~85% |
| `api/catalogos.py` | 19 tests | 100% |
| `api/personas.py` | 16 tests | ~90% |
| `api/visitas.py` | 14 tests | 100% |
| `api/events.py` | 13 tests | 100% |
| `api/acceso.py` | 14 tests | ~85% (depende de rostro) |

**Total: ~165 tests**

---

---

## Inventario completo de pruebas

### `unit/test_models.py` — Modelos ORM (23 tests)

#### `TestAreaModel` — Modelo `Area`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_seed_areas_existen` | Los catálogos precargados por `conftest` están en la BD | `len(areas) >= 3` |
| `test_area_tiene_nombre` | Cada área tiene campo `nombre` no nulo | Todos los nombres son truthy |
| `test_area_nombre_unico` | Insertar dos áreas con el mismo nombre viola UNIQUE | `IntegrityError` al hacer commit |
| `test_area_relacion_cargos` | La relación ORM `area.cargos` carga los cargos asociados | `len(area.cargos) >= 3` para "Tecnología" |

#### `TestCargoModel` — Modelo `Cargo`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_seed_cargos_existen` | Los cargos precargados están en la BD | `count >= 9` |
| `test_cargo_pertenece_a_area` | Cada cargo tiene `cargo.area` no nula | Todos los cargos tienen área |
| `test_cargo_fk_area_requerida` | Cargo con `id_area=99999` (inexistente) queda huérfano en SQLite | `cargo.area is None` (SQLite sin FK enforcement) o `IntegrityError` en BD con FK |

#### `TestTipoPersonaModel` — Modelo `TipoPersona`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_seed_tipos_existen` | Los 3 tipos base existen | `{"Empleado","Visitante","Contratista"} ⊆ tipos` |
| `test_empleado_flag_verdadero` | El flag `es_empleado` es correcto por tipo | Empleado=`True`, Visitante=`False`, Contratista=`False` |
| `test_tipo_nombre_unico` | Dos tipos con el mismo nombre violan UNIQUE | `IntegrityError` al hacer commit |

#### `TestPersonaModel` — Modelo `Persona`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_crear_visitante` | Visitante sin cargo se crea válido | `id_persona` asignado, `activo=True`, `id_cargo=None` |
| `test_crear_empleado_con_cargo` | Empleado con cargo asigna FK correctamente | `p.cargo.nombre == "Desarrollador Backend"` |
| `test_fecha_registro_auto` | `fecha_registro` se genera automáticamente | `isinstance(p.fecha_registro, datetime)` |
| `test_nro_documento_unico` | Dos personas con mismo documento violan UNIQUE | `IntegrityError` al hacer commit |
| `test_activo_default_true` | `activo` es `True` por defecto | `p.activo is True` |
| `test_relacion_tipo_persona` | La relación ORM `p.tipo_persona` carga el tipo correcto | `p.tipo_persona.tipo == "Visitante"` |

#### `TestRegistroModel` — Modelo `Registro`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_crear_registro_tipo_registro` | Insertar registro de alta de embedding | `evento=="registro"`, `len(embedding_facial)==2048` |
| `test_crear_registro_tipo_acceso` | Insertar registro de acceso con similitud | `tipo_acceso=="entrada"`, `similitud≈0.87` |
| `test_cascade_delete_persona_borra_registros` | Eliminar persona elimina sus registros en cascada | `count==0` tras `db.delete(p)` |
| `test_relacion_persona_cargada` | `registro.persona` carga la entidad correcta | `reg.persona.nombres == p.nombres` |

#### `TestVisitaModel` — Modelo `Visita`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_crear_visita` | Visita activa se crea con `fecha_salida=None` | `id_visita` asignado, `fecha_salida is None` |
| `test_registrar_salida` | Actualizar `fecha_salida` cierra la visita | `fecha_salida is not None` tras commit |
| `test_cascade_delete_persona_borra_visitas` | Eliminar persona elimina sus visitas en cascada | `count==0` tras `db.delete(p)` |
| `test_relacion_persona_en_visita` | `visita.persona` retorna la persona correcta | `v.persona.id_persona == p.id_persona` |

---

### `unit/test_database.py` — Capa de base de datos (14 tests)

#### `TestInitDb` — Creación de tablas y carga inicial de datos

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_crea_todas_las_tablas` | `create_all` genera las 6 tablas del esquema | `{"areas","cargos","tipos_persona","personas","registros","visitas"} ⊆ tablas` |
| `test_seed_inserta_tipos_persona` | La carga inicial crea los 3 tipos de persona | `count == 3` |
| `test_seed_inserta_area_y_cargo` | La carga inicial crea al menos 1 área y 1 cargo | `count >= 1` en ambas tablas |

#### `TestSeedIdempotencia` — Idempotencia de `_seed` (no duplica datos al ejecutarse varias veces)

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_segunda_siembra_no_duplica_tipos` | Ejecutar `_seed` dos veces no duplica tipos de persona | `count == 3` (igual al primer run) |
| `test_segunda_siembra_no_duplica_areas` | Ejecutar `_seed` dos veces no duplica áreas en la BD | `count == 1` |

#### `TestResetDb` — Limpieza de datos transaccionales

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_reset_borra_personas` | `reset_db` elimina todas las personas | `count == 0` |
| `test_reset_borra_registros` | `reset_db` elimina todos los registros | `count == 0` |
| `test_reset_borra_visitas` | `reset_db` elimina todas las visitas | `count == 0` |
| `test_reset_preserva_tipos_persona` | `reset_db` no toca los tipos de persona | `count == 3` |
| `test_reset_preserva_areas` | `reset_db` no toca las áreas | `count >= 1` |
| `test_reset_preserva_cargos` | `reset_db` no toca los cargos | `count >= 1` |

#### `TestGetDb` — Generador `get_db`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_get_db_retorna_sesion` | `get_db()` produce una sesión SQLAlchemy | `isinstance(db, Session)` |
| `test_get_db_cierra_sesion_al_finalizar` | Tras agotar el generador la sesión se cierra | `db.in_transaction() == False` |

---

### `unit/test_face_utils.py` — Utilidades matemáticas de ML (23 tests)

#### `TestNormalize` — Función `_normalize`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_norma_1_tras_normalizar` | El vector normalizado tiene norma ≈ 1 | `abs(norm - 1.0) < 1e-6` |
| `test_vector_cero_sin_modificar` | Un vector de ceros se retorna sin modificar (evita div/0) | `np.allclose(out, zeros)` |
| `test_vector_512_dims` | Normalizar 512-d retorna el mismo tamaño | `out.shape == (512,)` |
| `test_idempotencia` | Normalizar un vector ya normalizado no lo cambia | `np.allclose(v, _normalize(v))` |

#### `TestCosineSimilarity` — Función `cosine_similarity`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_mismo_vector_similitud_1` | Un vector comparado consigo mismo da 1.0 | `abs(sim - 1.0) < 1e-5` |
| `test_vectores_ortogonales_similitud_0` | Vectores ortogonales dan 0.0 | `sim == 0.0` |
| `test_similitud_en_rango_0_1` | La similitud siempre está en [0, 1] para 20 pares aleatorios | `0.0 <= sim <= 1.0` para todos |
| `test_similitud_simetrica` | `sim(a,b) == sim(b,a)` | Diferencia `< 1e-6` |
| `test_similitud_alta_para_vectores_cercanos` | Vectores con ruido ≈0.01 tienen similitud > 0.90 | `sim > 0.90` |
| `test_similitud_baja_para_vectores_distintos` | Dos vectores aleatorios independientes tienen similitud < 0.95 | `sim < 0.95` |

#### `TestEmbeddingSerialization` — `embedding_to_bytes` / `bytes_to_embedding`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_roundtrip_preserva_valores` | Serializar y deserializar retorna valores idénticos | `np.allclose(emb, emb2, atol=1e-7)` |
| `test_longitud_bytes_2048` | 512 float32 ocupan exactamente 2048 bytes | `len(data) == 2048` |
| `test_tipo_retorno_es_bytes` | `embedding_to_bytes` retorna `bytes` | `isinstance(data, bytes)` |
| `test_tipo_retorno_es_ndarray` | `bytes_to_embedding` retorna `ndarray float32` | `emb2.dtype == float32` |
| `test_copia_independiente` | `bytes_to_embedding` retorna copia, no vista del buffer | Modificar `emb2[0]` no altera `data` |
| `test_dimension_correcta` | El array deserializado tiene 512 dimensiones | `emb2.shape == (512,)` |

#### `TestFindBestMatch` — Función `find_best_match`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_lista_vacia_retorna_none` | Sin candidatos retorna `None` | `result is None` |
| `test_umbral_no_superado_retorna_none` | Similitud por debajo del umbral retorna `None` | `result is None` |
| `test_match_exacto` | Candidato idéntico al query retorna similitud ≈ 1.0 | `id==42`, `sim >= 0.9999` |
| `test_mejor_candidato_seleccionado` | Con múltiples candidatos retorna el de mayor similitud | `result[0] == 2` (el más cercano) |
| `test_similitud_redondeada_a_4_decimales` | La similitud retornada tiene máximo 4 decimales | `sim == round(sim, 4)` |
| `test_umbral_exacto_pasa` | Si `sim == threshold` el match es aceptado | `result is not None` |
| `test_multiples_candidatos_umbral_alto` | Con umbral 0.99 solo pasa el candidato casi idéntico | `result[0] == 20` |

---

### `api/test_catalogos.py` — Endpoints de catálogos (27 tests)

#### `TestListarAreas` — `GET /api/v1/catalogos/areas`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_status_200` | El endpoint existe y responde | `status_code == 200` |
| `test_retorna_lista` | El cuerpo es una lista JSON | `isinstance(body, list)` |
| `test_contiene_al_menos_3_areas` | Los catálogos precargados incluyen ≥ 3 áreas | `len(body) >= 3` |
| `test_campos_requeridos` | Cada área tiene `id_area` y `nombre` | Todos los items tienen ambas claves |
| `test_areas_ordenadas_alfabeticamente` | Las áreas vienen en orden alfabético | `nombres == sorted(nombres)` |
| `test_incluye_tecnologia` | "Tecnología" está entre las áreas precargadas | `"Tecnología" in nombres` |
| `test_id_area_entero_positivo` | Los `id_area` son enteros positivos | `isinstance(id, int) and id > 0` |

#### `TestListarCargosPorArea` — `GET /api/v1/catalogos/areas/{id}/cargos`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_status_200_area_valida` | Área existente responde 200 | `status_code == 200` |
| `test_retorna_lista` | El cuerpo es una lista | `isinstance(body, list)` |
| `test_cargos_tienen_campos` | Cada cargo tiene `id_cargo`, `nombre`, `id_area` | Todas las claves presentes |
| `test_todos_cargos_pertenecen_al_area` | Todos los cargos tienen el `id_area` solicitado | `cargo["id_area"] == area_id` para todos |
| `test_area_sin_cargos_retorna_lista_vacia` | Área con `id=9999` (inexistente) retorna lista vacía | `body == []` |
| `test_tecnologia_tiene_3_cargos` | "Tecnología" tiene exactamente 3 cargos precargados | `len(body) == 3` |
| `test_cargos_ordenados_alfabeticamente` | Los cargos vienen en orden alfabético | `nombres == sorted(nombres)` |

#### `TestListarTodosCargos` — `GET /api/v1/catalogos/cargos`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_status_200` | El endpoint responde | `status_code == 200` |
| `test_retorna_lista` | El cuerpo es lista | `isinstance(body, list)` |
| `test_contiene_9_cargos` | El `conftest` precarga 9 cargos (3 por área × 3 áreas) | `len(body) >= 9` |
| `test_campos_requeridos` | Cada cargo tiene `id_cargo`, `nombre`, `id_area` | Todas las claves presentes |
| `test_incluye_desarrollador_backend` | "Desarrollador Backend" está entre los cargos | `"Desarrollador Backend" in nombres` |

#### `TestListarTiposPersona` — `GET /api/v1/catalogos/tipos-persona`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_status_200` | El endpoint responde | `status_code == 200` |
| `test_retorna_lista` | El cuerpo es lista | `isinstance(body, list)` |
| `test_contiene_3_tipos` | Los 3 tipos base existen | `len(body) >= 3` |
| `test_campos_requeridos` | Cada tipo tiene `id_tipo_persona`, `tipo`, `es_empleado` | Todas las claves presentes |
| `test_tipos_esperados` | Empleado, Visitante y Contratista existen | `{"Empleado","Visitante","Contratista"} ⊆ tipos` |
| `test_empleado_tiene_flag_true` | `Empleado.es_empleado == True` | `es_empleado is True` |
| `test_visitante_tiene_flag_false` | `Visitante.es_empleado == False` | `es_empleado is False` |
| `test_ordenados_alfabeticamente` | Los tipos vienen en orden alfabético | `tipos == sorted(tipos)` |

---

### `api/test_personas.py` — Endpoints de personas (26 tests)

#### `TestCrearPersona` — `POST /api/v1/personas/`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_crear_visitante_ok` | Crear visitante retorna 200 con datos completos | `id_persona > 0`, `tipo=="Visitante"`, `activo==True` |
| `test_crear_empleado_ok` | Crear empleado con cargo retorna 200 | `id_persona > 0`, `tipo=="Empleado"`, `id_cargo!=None` |
| `test_crear_contratista_sin_cargo` | Contratista sin cargo es válido | `status==200`, `tipo=="Contratista"` |
| `test_documento_duplicado_409` | Documento ya existente retorna conflicto | `status_code == 409` |
| `test_tipo_persona_invalido_400` | `id_tipo_persona=99999` inexistente retorna error | `status_code == 400` |
| `test_empleado_sin_cargo_400` | Empleado sin cargo retorna error de validación | `status_code == 400` |
| `test_nombres_limpiados` | Nombres con espacios al inicio/final se limpian | `nombres == "Juan Pérez"` (sin espacios extra) |
| `test_n_embeddings_cero_al_crear` | Al crear, `n_embeddings` empieza en 0 | `n_embeddings == 0` |
| `test_campos_respuesta_completos` | La respuesta incluye todos los campos de `PersonaOut` | 11 campos presentes en el JSON |

#### `TestListarPersonas` — `GET /api/v1/personas/`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_lista_vacia_sin_personas` | BD vacía retorna lista vacía | `body == []` |
| `test_lista_con_persona_creada` | Una persona aparece en la lista | `len(body) >= 1` |
| `test_filtro_por_tipo_visitante` | `?tipo=Visitante` filtra solo visitantes | Todos con `tipo=="Visitante"` |
| `test_filtro_por_tipo_empleado` | `?tipo=Empleado` filtra solo empleados | Todos con `tipo=="Empleado"` |
| `test_ordenados_por_nombre` | La lista viene ordenada alfabéticamente | `nombres == sorted(nombres)` |
| `test_tipo_inexistente_retorna_vacio` | `?tipo=TipoQueNoExiste` retorna lista vacía | `body == []` |

#### `TestObtenerPersona` — `GET /api/v1/personas/{id}`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_persona_existente_200` | ID existente retorna 200 | `status_code == 200` |
| `test_datos_correctos` | La respuesta contiene los datos correctos | `nro_documento=="DET002"`, `nombres=="Juan Detalle"` |
| `test_persona_inexistente_404` | ID inexistente retorna 404 | `status_code == 404` |
| `test_empleado_incluye_cargo_y_area` | Respuesta del empleado incluye cargo y área | `cargo != None` y `area != None` |

#### `TestIdentificarPorCara` — `POST /api/v1/personas/identificar`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_imagen_sin_rostro_400` | Bytes JPEG inválidos retornan error | `status_code in (400, 422)` |
| `test_imagen_blanca_sin_match` | Imagen blanca sin galería retorna no encontrado | `status in (200,400)` / si 200: `encontrado==False` |
| `test_galeria_vacia_retorna_no_encontrado` | Sin personas registradas retorna no encontrado | `status in (200,400)` / si 200: `encontrado==False` |

#### `TestAgregarEmbedding` — `POST /api/v1/personas/{id}/registros`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_persona_inexistente_404` | ID inexistente retorna 404 | `status_code == 404` |
| `test_imagen_sin_rostro_retorna_ok_false` | Imagen blanca retorna `ok=False` con motivo | `ok==False`, `motivo=="rostro_no_detectado"` |
| `test_n_embeddings_no_cambia_con_imagen_invalida` | Sin rostro detectado `n_embeddings` no sube | `n_embeddings == 0` |
| `test_con_imagen_real_ok_o_sin_rostro` | Con imagen real retorna `ok` y `n_embeddings` | `"ok" in data`, `isinstance(n_embeddings, int)` |

---

### `api/test_visitas.py` — Endpoints de visitas (20 tests)

#### `TestCrearVisita` — `POST /api/v1/visitas/`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_crear_visita_visitante_ok` | Visita para visitante retorna 200 con `id_visita` | `id_visita > 0`, `id_persona` correcto |
| `test_crear_visita_contratista_ok` | Visita para contratista retorna 200 | `status_code == 200` |
| `test_persona_inexistente_404` | Persona con `id=99999` retorna 404 | `status_code == 404` |
| `test_empleado_no_puede_tener_visita_400` | Empleado no puede tener visita | `status_code == 400` |
| `test_motivo_trimmed` | El motivo se guarda sin espacios al inicio/final | `motivo == "Visita técnica"` |
| `test_respuesta_incluye_nombres` | La respuesta incluye el nombre de la persona | `nombres == "Carlos Ruiz"` |
| `test_respuesta_incluye_fecha` | La respuesta incluye la fecha de la visita | `fecha is not None` |
| `test_crear_visita_genera_registro_acceso` | Crear visita genera automáticamente un registro `entrada` | Al menos 1 evento de entrada para esa persona |

#### `TestListarVisitas` — `GET /api/v1/visitas/`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_lista_vacia_sin_visitas` | BD vacía retorna lista vacía | `body == []` |
| `test_visita_aparece_en_lista` | La visita creada aparece en el listado | `id_persona` presente en la lista |
| `test_filtro_por_persona` | `?id_persona=X` retorna solo visitas de esa persona | Todos con `id_persona == X` |
| `test_campos_respuesta` | Cada visita tiene todos los campos requeridos | 6 campos presentes (`id_visita`, `id_persona`, `nombres`, `motivo`, `fecha`, `fecha_salida`) |
| `test_fecha_salida_nula_visita_activa` | Visita recién creada tiene `fecha_salida=null` | `fecha_salida is None` |
| `test_max_100_visitas` | El endpoint no retorna más de 100 visitas | `len(body) <= 100` |
| `test_ordenadas_por_fecha_desc` | Las visitas vienen de la más reciente a la más antigua | `visitas[0].fecha >= visitas[1].fecha` |

#### `TestRegistrarSalida` — `PATCH /api/v1/visitas/{id}/salida`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_registrar_salida_ok` | Visita activa cierra correctamente | `status==200`, `fecha_salida != None` |
| `test_visita_inexistente_404` | ID inexistente retorna 404 | `status_code == 404` |
| `test_salida_idempotente_segunda_vez` | Registrar salida dos veces retorna 200 ambas veces | Ambos `status == 200` |
| `test_fecha_salida_es_timestamp` | `fecha_salida` es un string ISO 8601 | `isinstance(fecha_salida, str)` y `len > 10` |
| `test_visita_cerrada_no_aparece_en_activas` | La visita cerrada tiene `fecha_salida != null` al releer | `fecha_salida is not None` en el GET siguiente |

---

### `api/test_events.py` — Endpoints de eventos (19 tests)

#### `TestListarEventos` — `GET /api/v1/events/`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_status_200_sin_datos` | BD vacía responde 200 con lista | `status==200`, `isinstance(body, list)` |
| `test_evento_aparece_en_lista` | Registro de acceso insertado aparece en el listado | `id_persona` presente entre los eventos |
| `test_campos_respuesta` | Cada evento tiene los campos requeridos | 6 campos: `id_registro`, `id_persona`, `nombres`, `tipo_acceso`, `similitud`, `fecha` |
| `test_filtro_tipo_entrada` | `?tipo=entrada` retorna solo entradas | Todos con `tipo_acceso=="entrada"` |
| `test_filtro_tipo_salida` | `?tipo=salida` retorna solo salidas | Todos con `tipo_acceso=="salida"` |
| `test_filtro_tipo_invalido_retorna_todos` | `?tipo=invalido` retorna todos los eventos sin filtrar | `len(invalido) == len(todos)` |
| `test_paginacion_limit` | `?limit=3` restringe la cantidad de resultados | `len(body) <= 3` |
| `test_paginacion_offset` | `?offset=2` desplaza los resultados | `len(offset) == len(todos) - 2` |
| `test_limit_invalido_422` | `?limit=0` (fuera del rango `ge=1`) retorna error de validación | `status_code == 422` |
| `test_limit_maximo_500` | `?limit=500` es el máximo permitido | `status_code == 200` |
| `test_limit_sobre_maximo_422` | `?limit=501` supera el máximo | `status_code == 422` |
| `test_solo_eventos_de_acceso_sin_registros` | Registros de tipo `"registro"` (alta de embedding) no aparecen | Todos con `tipo_acceso in ("entrada","salida")` |
| `test_similitud_en_respuesta` | El campo `similitud` refleja el valor guardado | `abs(similitud - 0.92) < 1e-3` |
| `test_orden_descendente_por_fecha` | Los eventos vienen del más reciente al más antiguo | `fechas == sorted(fechas, reverse=True)` |

#### `TestAccesosHoy` — `GET /api/v1/events/hoy`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_status_200` | El endpoint existe y responde | `status_code == 200` |
| `test_campos_respuesta` | La respuesta incluye `fecha` y `total` | Ambas claves presentes |
| `test_total_es_entero_no_negativo` | `total` es un entero ≥ 0 | `isinstance(total, int)` y `total >= 0` |
| `test_fecha_formato_yyyy_mm_dd` | `fecha` tiene formato `YYYY-MM-DD` | Regex `\d{4}-\d{2}-\d{2}` coincide |
| `test_total_incrementa_con_nuevo_acceso` | Insertar un acceso hoy incrementa `total` en 1 | `total1 == total0 + 1` |

---

### `api/test_acceso.py` — Pipeline completo de acceso facial (13 tests)

#### `TestAccesoFallos` — Casos de fallo en `POST /api/v1/acceso/validar`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_imagen_vacia_400` | Imagen de 0 bytes retorna 400 | `status_code == 400` |
| `test_bytes_invalidos_retorna_sin_rostro` | Bytes que no son imagen retornan acceso denegado | `status in (200,400)` / si 200: `permitido==False` |
| `test_imagen_blanca_sin_galeria_retorna_no_permitido` | BD vacía + imagen blanca no concede acceso | `status in (200,400)` / si 200: `permitido==False` |
| `test_galeria_vacia_retorna_sin_personas_registradas` | Sin personas con embeddings en BD el motivo es `sin_personas_registradas` o `rostro_no_detectado` | `permitido==False`, `motivo in ("rostro_no_detectado","sin_personas_registradas")` |
| `test_motivo_persona_no_identificada_con_embedding_diferente` | Embedding de galería muy distinto al de la imagen no concede acceso | `permitido==False` |
| `test_respuesta_estructura_cuando_no_permitido` | La respuesta de denegado tiene la estructura correcta | Campos `permitido`, `motivo`, `persona`, `similitud` presentes |

#### `TestAccesoConRostroReal` — Pipeline completo con `face.jpg`
> Requieren `assets/face.jpg` con rostro detectable. Se saltan con `pytest.skip` si no hay rostro.

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_cara_detectada_match_en_galeria` | Embedding extraído de la imagen + mismo embedding en galería → acceso concedido | `permitido==True`, `tipo_acceso=="entrada"`, `id_persona` correcto |
| `test_respuesta_completa_cuando_permitido` | Respuesta de acceso concedido tiene todos los campos | `{permitido, tipo_acceso, similitud, persona}` presentes; persona tiene `id_persona` y `nombres` |
| `test_primera_deteccion_es_entrada` | Primera detección del día siempre es `entrada` | `tipo_acceso == "entrada"` |
| `test_similitud_en_rango_valido` | La similitud retornada está en [0, 1] | `0.0 <= similitud <= 1.0` |
| `test_acceso_queda_registrado_en_bd` | El evento de acceso queda persistido en `registros` | `count >= 1` en la tabla `registros` con `evento="acceso"` |

#### `TestAprendizajeProgresivo`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_acceso_alta_confianza_agrega_embedding` | Acceso con similitud ≥ `FACE_HIGH_CONFIDENCE_THRESHOLD` agrega el embedding a la galería | `n_registros_despues >= n_registros_antes` |

#### `TestCierreVisita`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_visita_se_cierra_cuando_visitante_sale` | Segundo acceso del visitante (`entrada`→`salida`) cierra automáticamente su visita activa | `visita.fecha_salida is not None` |

---

### `ml/test_hf_model.py` — Modelo HuggingFace (11 tests) `[slow]`

#### `TestHFModelCarga`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_instancia_correcta` | `_load_model()` retorna `_HFModel` cuando HF está disponible | `isinstance(model, _HFModel)` |
| `test_tiene_modelo_backbone` | El backbone Wide-ResNet-101-2 está cargado | `model._model is not None` |
| `test_tiene_sesion_yolo` | La sesión ONNX del detector YOLO está cargada | `model._yolo is not None` |
| `test_tiene_transform` | El pipeline de transformación de imagen está listo | `model._transform is not None` |
| `test_dispositivo_cpu` | El modelo opera en CPU | `model._device == torch.device("cpu")` |

#### `TestHFModelSinRostro`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_imagen_blanca_retorna_none` | Imagen blanca no supera el detector YOLO | `result is None` |
| `test_imagen_negra_retorna_none` | Imagen negra no supera el detector YOLO | `result is None` |
| `test_imagen_ruido_retorna_none_o_array` | Imagen de ruido uniforme no detecta rostro normalmente | `result is None` o `result.shape == (512,)` |

#### `TestHFModelConRostro`
> Se saltan si `face.jpg` no tiene rostro detectable.

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_embedding_dimension_512` | El embedding tiene exactamente 512 dimensiones | `result.shape == (512,)` |
| `test_embedding_dtype_float32` | El embedding es float32 | `result.dtype == float32` |
| `test_embedding_normalizado` | El embedding tiene norma L2 ≈ 1.0 | `abs(norm - 1.0) < 1e-5` |
| `test_embedding_determinista` | La misma imagen produce el mismo embedding en dos llamadas | `np.allclose(e1, e2, atol=1e-6)` |
| `test_embeddings_misma_persona_alta_similitud` | La misma imagen dos veces da similitud ≈ 1.0 | `cosine_similarity(e1, e2) > 0.99` |

#### `TestDetectFace`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_detect_face_imagen_blanca_retorna_none` | YOLO no detecta nada en imagen blanca | `result is None` |
| `test_detect_face_imagen_negra_retorna_none` | YOLO no detecta nada en imagen negra | `result is None` |
| `test_detect_face_retorna_array_o_none` | `_detect_face` retorna `ndarray uint8` del recorte o `None` | `result is None` o `result.dtype == uint8` |

---

### `ml/test_fallback_model.py` — Modelo DeepFace Facenet512 (10 tests) `[slow]`

#### `TestFallbackModelCarga`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_instancia_creada` | `_FallbackModel()` se instancia sin errores | `isinstance(model, _FallbackModel)` |
| `test_tiene_deepface` | El atributo `_df` apunta al módulo DeepFace | `model._df is DeepFace` |

#### `TestFallbackSinRostro`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_imagen_blanca_retorna_none` | Imagen blanca no tiene rostro | `result is None` |
| `test_imagen_negra_retorna_none` | Imagen negra no tiene rostro | `result is None` |
| `test_no_lanza_excepcion_sin_rostro` | DeepFace captura excepciones internamente, no propaga | No se lanza excepción; `result is None` o `ndarray` |

#### `TestFallbackConRostro`
> Se saltan si `face.jpg` no tiene rostro detectable.

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_embedding_dimension_512` | El embedding tiene 512 dimensiones | `result.shape == (512,)` |
| `test_embedding_dtype_float32` | El embedding es float32 | `result.dtype == float32` |
| `test_embedding_normalizado` | El embedding tiene norma L2 ≈ 1.0 | `abs(norm - 1.0) < 1e-5` |
| `test_embedding_determinista` | La misma imagen produce el mismo embedding en dos llamadas | `np.allclose(e1, e2, atol=1e-5)` |
| `test_similitud_misma_imagen` | La misma imagen comparada consigo misma da similitud ≈ 1.0 | `cosine_similarity(e1, e2) > 0.99` |

---

### `ml/test_pipeline.py` — Pipeline público (12 tests) `[slow]`

#### `TestGetModel` — Singleton `get_model()`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_retorna_instancia` | `get_model()` retorna `_HFModel` o `_FallbackModel` | `isinstance(model, (_HFModel, _FallbackModel))` |
| `test_singleton_misma_referencia` | Dos llamadas a `get_model()` retornan la misma instancia | `m1 is m2` |
| `test_tiene_metodo_get_embedding` | El modelo tiene el método `get_embedding` | `callable(model.get_embedding)` |
| `test_tipo_es_hf_o_fallback` | Solo existen dos tipos de modelo posibles | `type(model).__name__ in ("_HFModel","_FallbackModel")` |

#### `TestGetEmbeddingFromBytes` — `get_embedding_from_bytes()`

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_bytes_invalidos_retorna_none` | Bytes que no son imagen retornan `None` | `result is None` |
| `test_bytes_vacios_retorna_none` | Bytes vacíos retornan `None` | `result is None` |
| `test_imagen_blanca_retorna_none` | Imagen blanca sin rostro retorna `None` | `result is None` |
| `test_con_imagen_real_retorna_ndarray_o_none` | Imagen real retorna `ndarray 512-d` o `None` | `result is None` o `result.shape == (512,)` |
| `test_embedding_float32` | El embedding tiene dtype float32 | `result.dtype == float32` |
| `test_embedding_normalizado` | El embedding tiene norma ≈ 1.0 | `abs(norm - 1.0) < 1e-5` |
| `test_imagen_png_tambien_funciona` | Las imágenes PNG se procesan igual que JPEG | `result is None` o `isinstance(result, ndarray)` |
| `test_determinismo_doble_llamada` | La misma imagen produce el mismo embedding en dos llamadas | `np.allclose(e1, e2, atol=1e-5)` |

#### `TestPipelineCompleto` — Integración extremo a extremo

| Test | Qué prueba | Salida esperada |
|------|-----------|-----------------|
| `test_embedding_real_encuentra_match_en_galeria` | Embedding de `face.jpg` encuentra su match en galería con umbral 0.95 | `result[0] == 999` (ID del match correcto) |
| `test_embedding_no_coincide_con_galeria_distinta` | Embedding real no coincide con 10 vectores aleatorios | `result is None` o `result[1] < 0.9` |
| `test_serializar_y_recuperar_embedding` | Round-trip bytes → BD → recuperación preserva el embedding | `np.allclose(emb, recuperado)`, `sim > 0.9999` |
| `test_similitud_entre_versiones_misma_imagen` | Dos extracciones de la misma imagen tienen similitud muy alta | `cosine_similarity(e1, e2) > 0.99` |

---

## Solución de problemas

### `ModuleNotFoundError: No module named 'backend'`

Ejecutar siempre desde la raíz del proyecto:

```powershell
# Desde d:\study\proyectos_ai\sca-empx\
uv run pytest backend/tests/ -v
```

### Tests ML fallan con `OSError` o `ConnectionError`

El modelo HuggingFace necesita descargar sus pesos la primera vez:

```powershell
# Verificar que los pesos están en caché
Get-ChildItem .cache\face_recognition\
```

Si el directorio `.cache/face_recognition/` contiene `pytorch_model.bin` y `yolov8s-face-lindevs.onnx`, los modelos ya están descargados.

### Tests de acceso saltan con `pytest.skip`

La imagen de test `assets/face.jpg` no contiene un rostro detectable por YOLO o MTCNN. Ver [assets/README.md](assets/README.md) para instrucciones de reemplazo.

### `IntegrityError` en tests de API

Las tablas de catálogo están compartidas entre tests y no se limpian. Si algún test inserta un área/cargo/tipo con nombre duplicado, usa nombres únicos (con prefijo único por test).
