# Tareas de desarrollo por Historia de Usuario

Tareas puntuales y objetivas asociadas a cada HU, para desarrollo del software y carga en Azure DevOps (como ítems Task bajo cada User Story).

**Alcance:** MVP (reconocimiento facial con librería pre-entrenada, FastAPI/Flask, SQLite/PostgreSQL, frontend simple). Referencia: [08-definicion-proyecto.md](./08-definicion-proyecto.md).

---

## HU-01 – Registrar Empleado

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Definir esquema BD: tabla `persona` (id, nombre_completo, documento, cargo, área, tipo_persona, estado, fecha_registro) | Backend |
| 2 | Definir tabla `reconocimiento_facial` (id_persona, embedding, modelo_version, estado) | Backend |
| 3 | Implementar POST /api/personas: recibir JSON (nombre, documento, cargo, área, tipo) + foto (multipart/base64) | Backend |
| 4 | Integrar librería de reconocimiento facial: detección de rostro y generación de embedding (face_recognition/DeepFace/MediaPipe) | Backend |
| 5 | Validar documento único (no duplicado); retornar 409 si existe | Backend |
| 6 | Persistir persona + embedding; retornar id, estado activo y score de calidad (opcional) | Backend |
| 7 | Pantalla de registro: formulario (nombre, documento, cargo, área, tipo) + captura/carga de foto | Frontend |
| 8 | Conectar formulario a POST /api/personas; mostrar confirmación o error (ej. foto sin rostro) | Frontend |

---

## HU-02 – Desactivar Empleado

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Implementar PATCH /api/personas/{id} con cuerpo { "estado": "inactivo" } | Backend |
| 2 | Asegurar que validación de acceso (HU-05) rechace personas con estado inactivo | Backend |
| 3 | Pantalla/listado de personas con búsqueda por nombre o documento | Frontend |
| 4 | Botón/acción "Desactivar" que llame a PATCH y muestre confirmación | Frontend |

---

## HU-03 – Registrar Visitante

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Extender modelo persona con campos empresa, motivo_visita; opcional: id_empleado_visitado | Backend |
| 2 | Reutilizar POST /api/personas con tipo visitante; misma validación documento y flujo de foto/embedding | Backend |
| 3 | (Opcional MVP) GET /api/personas?tipo=empleado para listar empleados (selector “a quien visita”) | Backend |
| 4 | Pantalla registro visitante: formulario (nombre, documento, empresa, motivo) + foto; enviar a POST /api/personas | Frontend |

---

## HU-04 – Generar Autorización de Visita *(fuera del MVP)*

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Crear tabla `autorizacion` (id_persona, fecha_inicio, fecha_fin, estado) | Backend |
| 2 | Implementar POST /api/autorizaciones para crear autorización vigente | Backend |
| 3 | Pantalla: selector de visitante + fechas inicio/fin; enviar a POST /api/autorizaciones | Frontend |

*Estas tareas se implementan en iteración posterior al MVP.*

---

## HU-05 – Validar Acceso por Reconocimiento Facial (Método Principal)

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Implementar POST /api/validate-access: body con imagen (base64 o multipart) | Backend |
| 2 | En el endpoint: detectar rostro y generar embedding con la misma librería usada en registro | Backend |
| 3 | Comparar embedding con todos los activos en BD (similaridad coseno o distancia euclidiana); umbral configurable (ej. 0.6) | Backend |
| 4 | Si hay coincidencia: verificar persona activa; retornar { allowed, person_id, similarity, reason } | Backend |
| 5 | Si no hay coincidencia o persona inactiva: retornar allowed=false y reason | Backend |
| 6 | Llamar a registro de evento (entrada) cuando allowed=true (ver HU-06) | Backend |
| 7 | Página de prueba: subir foto o usar webcam; llamar POST /api/validate-access y mostrar resultado (permitido/denegado) | Frontend |

---

## HU-06 – Registrar Evento de Entrada

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Crear tabla `registro_acceso` (id_persona, fecha_hora, tipo_movimiento, resultado, similarity_score, metodo) | Backend |
| 2 | Implementar servicio/función que inserte registro (persona, entrada, permitido, score) | Backend |
| 3 | Invocar este registro desde POST /api/validate-access cuando el acceso sea permitido | Backend |
| 4 | (Opcional) GET /api/eventos incluya eventos de tipo entrada para listado | Backend |

---

## HU-07 – Registrar Evento de Salida

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Implementar POST /api/register-exit o incluir en validate-access tipo “salida”: recibe imagen, identifica persona, registra evento salida | Backend |
| 2 | Insertar en `registro_acceso` con tipo_movimiento=salida, resultado=permitido | Backend |
| 3 | (Opcional MVP) Página o botón “Registrar salida” que envíe foto y llame al endpoint de salida | Frontend |

---

## HU-08 – Consultar Historial de Accesos

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Implementar GET /api/eventos con query params: persona_id o documento, fecha_desde, fecha_hasta, tipo, resultado, limit, offset | Backend |
| 2 | Ordenar por fecha_hora descendente; paginación (ej. máximo 100 por página) | Backend |
| 3 | (Opcional) GET /api/eventos/export?formato=csv con mismos filtros | Backend |
| 4 | Pantalla de consulta: filtros (persona, rango fechas) + tabla de eventos + botón exportar CSV si existe | Frontend |

---

## HU-09 – Gestionar Usuarios del Sistema

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Crear tabla `usuario_sistema` (username, password_hash, rol, estado) | Backend |
| 2 | Implementar registro/login básico (JWT o sesión); middleware de autenticación para rutas protegidas | Backend |
| 3 | POST /api/usuarios para crear usuario (admin); GET /api/usuarios para listar | Backend |
| 4 | Pantalla de administración de usuarios: listado, formulario alta, activar/desactivar | Frontend |

*En MVP puede limitarse a un solo usuario administrador y login simple.*

---

## HU-10 – Actualizar Información de Empleado

| # | Tarea | Tipo |
|---|--------|------|
| 1 | Implementar PATCH /api/personas/{id} para actualizar nombre, cargo, área, tipo_contrato, contacto | Backend |
| 2 | En pantalla de listado/búsqueda de personas: abrir detalle y formulario de edición que llame a PATCH | Frontend |

---

## HU-11 – Ver Dashboard de Accesos

| # | Tarea | Tipo |
|---|--------|------|
| 1 | GET /api/eventos/recientes?minutos=10 para últimos eventos | Backend |
| 2 | GET /api/estadisticas o incluir en eventos: total dentro, accesos hoy, denegaciones hoy | Backend |
| 3 | Pantalla dashboard: tarjetas con métricas + lista de eventos recientes; actualización periódica (ej. cada 30 s) | Frontend |

---

## HU-12 – Generar Reporte de Accesos

| # | Tarea | Tipo |
|---|--------|------|
| 1 | GET /api/reportes/accesos?fecha_desde&fecha_hasta&formato=pdf|csv con datos agregados | Backend |
| 2 | Pantalla: selector de rango de fechas y tipo de reporte; botón descargar PDF/CSV | Frontend |

---

## HU-13 – Revocar Autorización *(fuera del MVP)*

| # | Tarea | Tipo |
|---|--------|------|
| 1 | PATCH /api/autorizaciones/{id} con estado=revocada; motivo opcional | Backend |
| 2 | Pantalla: listar autorizaciones activas por persona; botón revocar | Frontend |

---

## HU-14 – Consultar Personas Dentro de la Empresa

| # | Tarea | Tipo |
|---|--------|------|
| 1 | GET /api/personas/dentro: personas con al menos un registro entrada sin salida correspondiente en el mismo día | Backend |
| 2 | Pantalla: lista “Personas actualmente dentro” con nombre y hora de entrada | Frontend |

---

## Tareas transversales (no asociadas a una sola HU)

| # | Tarea | Nota |
|---|--------|------|
| 1 | Configurar proyecto backend (FastAPI o Flask), venv, dependencias (incl. librería reconocimiento facial) | Semana 1 |
| 2 | Configurar BD (SQLite dev / PostgreSQL opcional); migraciones o scripts de creación de tablas | Semana 2 |
| 3 | Autenticación básica (login) y protección de rutas de administración | Para HU-09 y uso del frontend |
| 4 | README: instalación, variables de entorno, cómo ejecutar backend y frontend | Cierre MVP |

---

**Uso en Azure DevOps:** Crear un ítem **Task** por cada fila de la tabla (o por cada viñeta), asignar **Parent** = User Story correspondiente (HU-01, HU-02, …), y opcionalmente **Iteration** (Semana 1, 2 o 3) según el cronograma del doc 08.

**Documento:** Tareas por HU  
**Versión:** 1.0  
**Proyecto:** SCA-EMPX – MVP
