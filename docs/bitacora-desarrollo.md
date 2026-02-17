# Bitácora de desarrollo - SCA-EMPX

Documento para **registrar el avance** del desarrollo del proyecto: check de actividades, orden de implementación y contexto. Referencia: [Orden de desarrollo y features](./orden-desarrollo-features.md), [Tareas por HU](./09-tareas-por-hu.md).

---

## Cómo usar esta bitácora

- **Check (✓)**: Marcar cuando la actividad o tarea esté hecha (reemplazar `[ ]` por `[x]` o anotar ✓).
- **Fecha**: Anotar fecha de inicio/fin o de check cuando lo uses.
- **Notas**: Línea breve de observaciones, bloqueos o decisiones (opcional).
- **Orden**: Respetar el orden de pasos (0 → 1 → 2 …) según [orden-desarrollo-features.md](./orden-desarrollo-features.md).

---

## Resumen de estado

| Paso | Rama / feature              | HU    | Estado      | Fecha (última actualización) |
|------|-----------------------------|-------|-------------|------------------------------|
| 0    | feature/setup-mvp           | —     | Hecho       | —                            |
| 1    | feature/hu-05-validar-acceso-facial | HU-05 | Hecho       | —                            |
| 2    | feature/hu-01-registrar-empleado    | HU-01 | Hecho       | 2026-02                      |
| 3    | feature/hu-03-registrar-visitante   | HU-03 | Hecho       | 2026-02                      |
| 4    | feature/hu-04-autorizacion-visita    | HU-04 | Hecho       | 2026-02                      |
| 5    | feature/hu-06-registro-evento-entrada| HU-06 | Hecho       | 2026-02                      |
| 6    | feature/hu-07-registro-evento-salida | HU-07 | Pendiente   | —                            |
| 7    | feature/hu-09-gestionar-usuarios     | HU-09 | Pendiente   | —                            |
| 8    | feature/hu-02-desactivar-empleado   | HU-02 | Pendiente   | —                            |
| 9    | feature/hu-08-historial-accesos      | HU-08 | Pendiente   | —                            |
| 10   | feature/hu-10-actualizar-empleado    | HU-10 | Pendiente   | —                            |
| 11   | feature/hu-11-dashboard-accesos      | HU-11 | Pendiente   | —                            |
| 12   | feature/hu-13-revocar-autorizacion   | HU-13 | Pendiente   | —                            |
| 13   | feature/hu-14-personas-dentro        | HU-14 | Pendiente   | —                            |
| 14   | feature/hu-12-reporte-accesos       | HU-12 | Pendiente   | —                            |

*Actualizar "Estado" (Pendiente / En curso / Hecho) y "Fecha" al avanzar.*

---

## Paso 0 – Setup MVP (transversal)

**Rama:** `feature/setup-mvp`  
**Objetivo:** Proyecto backend listo, BD SQLite, dependencias, estructura base.

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | Configurar proyecto backend (FastAPI), venv, pyproject.toml, dependencias | [x] | Estructura creada |
| 2 | Estructura de carpetas (api, core, db, schemas, services, ml) | [x] | |
| 3 | Configurar BD SQLite; scripts o migraciones de creación de tablas | [x] | init_db.py + SQLAlchemy + modelos |
| 4 | Autenticación básica (login) y protección de rutas (para HU-09) | [x] | JWT, login, get_current_user |
| 5 | README / documentación de instalación y ejecución | [x] | Sección Instalación y ejecución |

**Fecha inicio:** ___________  
**Fecha fin:** ___________  
**Notas:** ___________________________________________

---

## Paso 1 – HU-05: Validar acceso por reconocimiento facial

**Rama:** `feature/hu-05-validar-acceso-facial`

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | POST /api/validate-access (o /api/v1/access/validate): body con imagen | [x] | File upload en /api/v1/access/validate |
| 2 | Detectar rostro y generar embedding (misma librería que registro) | [x] | DeepFace Facenet en ml/inference.py |
| 3 | Comparar embedding con activos en BD; umbral configurable | [x] | SIMILARITY_THRESHOLD, FACE_DISTANCE_THRESHOLD |
| 4 | Si coincidencia: verificar persona activa; retornar allowed, person_id, similarity | [x] | access_service + response |
| 5 | Si no coincidencia o inactivo: retornar allowed=false y reason | [x] | reason: rostro_no_detectado, persona_no_identificada, etc. |
| 6 | Invocar registro de evento de entrada cuando allowed=true (HU-06) | [x] | _register_entrada en access_service |
| 7 | Página de prueba: subir foto/webcam → POST validate-access → resultado | [x] | GET /validate-access (HTML) |

**Fecha inicio:** ___________  
**Fecha fin:** ___________  
**Notas:** ___________________________________________

---

## Paso 2 – HU-01: Registrar empleado

**Rama:** `feature/hu-01-registrar-empleado`

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | Esquema BD: tabla persona (id, nombre_completo, documento, cargo, área, tipo_persona, estado, fecha_registro) | [x] | Ya en setup-mvp |
| 2 | Tabla reconocimiento_facial (id_persona, embedding, modelo_version, estado) | [x] | Ya en setup-mvp |
| 3 | POST /api/personas: JSON + foto (multipart/base64) | [x] | POST /api/v1/personas multipart Form + File |
| 4 | Integrar librería reconocimiento facial: detección rostro + embedding | [x] | DeepFace Facenet en persona_service |
| 5 | Validar documento único; 409 si existe | [x] | documento_duplicado → 409 |
| 6 | Persistir persona + embedding; retornar id, estado, score (opcional) | [x] | PersonaRegistroResponse |
| 7 | Pantalla registro: formulario + captura/carga de foto | [x] | GET /registro-empleado |
| 8 | Conectar formulario a POST /api/personas; confirmación o error | [x] | FormData → POST /api/v1/personas |

**Fecha inicio:** ___________  
**Fecha fin:** 2026-02  
**Notas:** Fix id_registro INTEGER (RegistroAcceso); scripts clear_personas, fix_registro_acceso; umbrales similitud configurables.

---

## Paso 3 – HU-03: Registrar visitante

**Rama:** `feature/hu-03-registrar-visitante`

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | Extender modelo persona: empresa, motivo_visita; opcional id_empleado_visitado | [x] | Persona.motivo_visita, id_empleado_visitado; ensure_persona_visitante_columns |
| 2 | Reutilizar POST /api/personas tipo visitante; mismo flujo foto/embedding | [x] | tipo=visitante_temporal; registrar_visitante() en persona_service |
| 3 | (Opcional) GET /api/personas?tipo=empleado para selector “a quien visita” | [x] | GET /api/v1/personas?tipo=empleado; también ?tipo=visitante |
| 4 | Pantalla registro visitante: formulario + foto → POST /api/personas | [x] | GET /registro-visitante (empresa, motivo, selector empleado, foto) |

**Fecha inicio:** ___________  
**Fecha fin:** 2026-02  
**Notas:** ___________________________________________

---

## Paso 4 – HU-04: Generar autorización de visita

**Rama:** `feature/hu-04-autorizacion-visita`  
*Puede posponerse en MVP estricto.*

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | Tabla autorizacion (id_persona, fecha_inicio, fecha_fin, estado) | [x] | Modelo Autorizacion; ensure_autorizacion_table al arranque |
| 2 | POST /api/autorizaciones para crear autorización vigente | [x] | POST /api/v1/autorizaciones JSON; solo visitantes activos |
| 3 | Pantalla: selector visitante + fechas → POST /api/autorizaciones | [x] | GET /autorizacion-visita (selector ?tipo=visitante, fecha inicio/fin) |

**Fecha inicio:** ___________  
**Fecha fin:** 2026-02  
**Notas:** GET /api/v1/autorizaciones lista todas; servicio valida fecha_fin > fecha_inicio.

---

## Paso 5 – HU-06: Registrar evento de entrada

**Rama:** `feature/hu-06-registro-evento-entrada`

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | Tabla registro_acceso (id_persona, fecha_hora, tipo_movimiento, resultado, similarity_score, metodo) | [x] | Ya existía (setup/HU-05) |
| 2 | Servicio/función que inserta registro (persona, entrada, permitido, score) | [x] | event_service.register_entrada(); access_service lo invoca |
| 3 | Invocar desde POST validate-access cuando acceso permitido | [x] | validate_access → register_entrada al permitir acceso |
| 4 | (Opcional) GET /api/eventos con eventos tipo entrada | [x] | GET /api/v1/events?tipo=ingreso; limit/offset; EventoListItem |

**Fecha inicio:** ___________  
**Fecha fin:** 2026-02  
**Notas:** Servicio eventos desacoplado; GET events con filtro tipo (ingreso/salida) y paginación (máx 100).

---

## Paso 6 – HU-07: Registrar evento de salida

**Rama:** `feature/hu-07-registro-evento-salida`

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | POST /api/register-exit o tipo “salida”: imagen → identifica persona → registra salida | [ ] | |
| 2 | Insertar en registro_acceso tipo_movimiento=salida, resultado=permitido | [ ] | |
| 3 | (Opcional) Pantalla/botón “Registrar salida” | [ ] | |

**Fecha inicio:** ___________  
**Fecha fin:** ___________  
**Notas:** ___________________________________________

---

## Paso 7 – HU-09: Gestionar usuarios del sistema

**Rama:** `feature/hu-09-gestionar-usuarios`

| # | Actividad | Check | Notas |
|---|-----------|--------|-------|
| 1 | Tabla usuario_sistema (username, password_hash, rol, estado) | [ ] | |
| 2 | Registro/login básico (JWT o sesión); middleware auth para rutas protegidas | [ ] | |
| 3 | POST /api/usuarios crear; GET /api/usuarios listar | [ ] | |
| 4 | Pantalla administración: listado, alta, activar/desactivar | [ ] | |

*MVP: puede limitarse a un usuario administrador y login simple.*

**Fecha inicio:** ___________  
**Fecha fin:** ___________  
**Notas:** ___________________________________________

---

## Pasos 8 a 14 – Resumen de check

| Paso | HU / feature | Actividades principales | Check global |
|------|--------------|-------------------------|--------------|
| 8 | HU-02 Desactivar empleado | PATCH personas/{id} inactivo; validación rechace inactivos; pantalla listado + Desactivar | [ ] |
| 9 | HU-08 Historial accesos | GET /api/eventos filtros + paginación; export CSV; pantalla consulta | [ ] |
| 10 | HU-10 Actualizar empleado | PATCH personas/{id}; pantalla detalle/edición | [ ] |
| 11 | HU-11 Dashboard accesos | GET eventos recientes + estadísticas; pantalla métricas + actualización periódica | [ ] |
| 12 | HU-13 Revocar autorización | PATCH autorizaciones/{id} revocada; pantalla listar activas + revocar | [ ] |
| 13 | HU-14 Personas dentro | GET /api/personas/dentro; pantalla lista “actualmente dentro” | [ ] |
| 14 | HU-12 Reporte accesos | GET reportes + filtros; export PDF/CSV; pantalla selector + descarga | [ ] |

*Desarrollar cada paso en su rama; integrar en `develop`; luego siguiente rama desde `develop`.*

---

## Registro de avance (entradas libres)

Anotar aquí hitos, decisiones, bloqueos o cambios de orden con fecha.

| Fecha | Entrada                                                                       |
|-------|-------------------------------------------------------------------------------|
|       | *Ejemplo: Estructura inicial creada. Rama main. Próximo: feature/setup-mvp.*  |
| 2026-02 | HU-01, HU-03, HU-04 implementados. Bitácora actualizada: Pasos 2, 3, 4 marcados Hecho; tareas con check y notas. |
| 2026-02 | HU-06 implementado: event_service.register_entrada, GET /api/v1/events (tipo, limit, offset). Bitácora Paso 5 actualizada. |
|       |                                                                               |
|       |                                                                               |
|       |                                                                               |

---

**Documento:** Bitácora de desarrollo  
**Versión:** 1.0  
**Fecha:** 2026  
**Proyecto:** SCA-EMPX – STI S.A.S.
