# Orden de desarrollo y registro de features - SCA-EMPX

## 1. Confirmación del contexto según la documentación

### Proyecto y alcance

- **Proyecto**: Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (**SCA-EMPX**) para STI S.A.S.
- **Fase**: **MVP** (Producto Mínimo Viable), **3 semanas**.

### Fuentes: toda la documentación en la carpeta `docs/`

El contexto del proyecto y el orden de desarrollo **se toman de toda la información contenida en la carpeta [`docs/`](./)**. Cada documento aporta lo siguiente:

| Documento | Contenido que aporta |
|-----------|------------------------|
| [00-indice.md](./00-indice.md) | Índice y navegación de toda la documentación. |
| [01-contexto-empresarial.md](./01-contexto-empresarial.md) | Empresa STI S.A.S., instalaciones, tipos de personas, necesidad del sistema. |
| [02-caso-de-negocio.md](./02-caso-de-negocio.md) | Justificación del proyecto, beneficios, ROI, riesgos de no implementar. |
| [03-requerimientos-srs.md](./03-requerimientos-srs.md) | Requerimientos funcionales (RF) y no funcionales (RNF), actores, restricciones. |
| [04-arquitectura.md](./04-arquitectura.md) | Diseño arquitectónico, componentes, tecnologías, flujos de datos. |
| [05-modelo-datos.md](./05-modelo-datos.md) | Esquema de base de datos, tablas, relaciones, índices. |
| [06-historias-usuario.md](./06-historias-usuario.md) | Historias de usuario, épicas, backlog priorizado y orden de sprints (Sprint 1, 2, 3…). |
| [07-procesos-bpmn.md](./07-procesos-bpmn.md) | Flujos de negocio: ingreso, salida, registro de visitante, desactivación. |
| [08-definicion-proyecto.md](./08-definicion-proyecto.md) | Objetivos del MVP, alcance incluido/excluido, cronograma de 3 semanas, tareas por fase. |
| [09-tareas-por-hu.md](./09-tareas-por-hu.md) | Tareas de desarrollo concretas por cada HU (backend/frontend) para implementación. |
| [guia-git.md](./guia-git.md) | Flujo de trabajo Git, ramas, ambientes (dev, UAT, producción), buenas prácticas. |
| [orden-desarrollo-features.md](./orden-desarrollo-features.md) | Este documento: orden para registrar features y confirmación de contexto. |

Para desarrollar de forma alineada al proyecto hay que considerar **toda** esta documentación: el orden de features y sprints sale de 06 y 09; el qué construir y con qué criterios, de 03 y 06; el cómo (arquitectura, modelo de datos, procesos), de 04, 05 y 07; y el por qué y el alcance, de 01, 02 y 08.

### Tecnologías MVP

- **Backend**: Python (FastAPI o Flask).
- **Reconocimiento facial**: Librería pre-entrenada (face_recognition, DeepFace o MediaPipe).
- **Base de datos**: SQLite (desarrollo) o PostgreSQL (opcional).
- **Frontend**: Interfaz web simple (React o HTML/CSS/JS).
- **Autenticación**: Básica (JWT o sesión) para administración.

### Respuesta directa

**Sí, se puede iniciar el desarrollo de manera paso a paso y en el orden indicado en las Historias de Usuario y en las Tareas por HU.**  
El orden recomendado es el del **backlog priorizado** del doc 06 (Sprints 1, 2, 3…) y, dentro de cada HU, el detalle de tareas del doc 09. Las features se pueden registrar (ramas Git, ítems en Azure DevOps) siguiendo la numeración y el orden de la tabla siguiente. Toda la carpeta `docs/` es la fuente de verdad para contexto, requerimientos, arquitectura, modelo de datos, procesos y alcance.

---

## 2. Orden recomendado para registrar features

Usa este orden tanto para **ramas Git** (`feature/hu-XX-nombre`) como para **User Stories / Tasks** en Azure DevOps. Cada fila es una feature que puedes registrar en secuencia.

| # | HU   | Nombre sugerido rama / feature | Descripción breve |
|---|------|---------------------------------|-------------------|
| 0 | —    | `feature/setup-mvp`            | Tareas transversales: proyecto backend (FastAPI/Flask), venv, dependencias, BD (SQLite), migraciones, auth básica. *Hacer primero.* |
| 1 | HU-05| `feature/hu-05-validar-acceso-facial` | Validar acceso por reconocimiento facial (método principal). POST /api/validate-access, detección rostro, embedding, comparación, respuesta permitido/denegado. |
| 2 | HU-01| `feature/hu-01-registrar-empleado`    | Registrar empleado: esquema persona + reconocimiento_facial, POST /api/personas con foto, embedding, pantalla de registro. |
| 3 | HU-03| `feature/hu-03-registrar-visitante`    | Registrar visitante: extender persona (empresa, motivo, empleado visitado), mismo flujo foto/embedding, pantalla registro visitante. |
| 4 | HU-04| `feature/hu-04-autorizacion-visita`    | Generar autorización de visita (tabla autorizacion, POST /api/autorizaciones, pantalla selector visitante + fechas). *Doc 09 la marca fuera MVP; si priorizas MVP estricto, puedes dejarla para después.* |
| 5 | HU-06| `feature/hu-06-registro-evento-entrada` | Registrar evento de entrada: tabla registro_acceso, servicio que inserta al permitir acceso, invocado desde validate-access. |
| 6 | HU-07| `feature/hu-07-registro-evento-salida`  | Registrar evento de salida: POST salida o tipo salida, insertar en registro_acceso, opcional pantalla “Registrar salida”. |
| 7 | HU-09| `feature/hu-09-gestionar-usuarios`       | Gestionar usuarios del sistema: tabla usuario_sistema, login/registro, POST/GET /api/usuarios, pantalla administración. *MVP puede ser un solo admin + login simple.* |
| 8 | HU-02| `feature/hu-02-desactivar-empleado`     | Desactivar empleado: PATCH /api/personas/{id} estado inactivo, que HU-05 rechace inactivos, pantalla listado + Desactivar. |
| 9 | HU-08| `feature/hu-08-historial-accesos`        | Consultar historial de accesos: GET /api/eventos con filtros y paginación, opcional export CSV, pantalla consulta. |
|10 | HU-10| `feature/hu-10-actualizar-empleado`      | Actualizar información de empleado: PATCH /api/personas/{id} (nombre, cargo, área, contacto), pantalla detalle/edición. |
|11 | HU-11| `feature/hu-11-dashboard-accesos`        | Dashboard de accesos: GET eventos recientes y estadísticas, pantalla con métricas y actualización periódica. |
|12 | HU-13| `feature/hu-13-revocar-autorizacion`     | Revocar autorización: PATCH /api/autorizaciones/{id} revocada. *Fuera MVP si aplica.* |
|13 | HU-14| `feature/hu-14-personas-dentro`          | Consultar personas dentro: GET /api/personas/dentro, pantalla lista “actualmente dentro”. |
|14 | HU-12| `feature/hu-12-reporte-accesos`          | Generar reporte de accesos: GET reportes con filtros, export PDF/CSV. Prioridad baja. |

---

## 3. Cómo usar este orden

### En Git

1. Crear y trabajar una rama por feature en el orden de la tabla (salvo que el equipo decida otro orden para una HU concreta).
2. Integrar en `develop` cuando la HU esté terminada (según [Guía de Git](./guia-git.md): `feature/xxx` → `develop` → `uat` → `main`).
3. Nombre de rama sugerido: `feature/hu-XX-nombre-corto` (ej. `feature/hu-01-registrar-empleado`).

### En Azure DevOps

1. Crear las **User Stories** en el mismo orden (HU-05, HU-01, HU-03, …) y asignar a la iteración correspondiente (Sprint 1, 2, 3 según [06-historias-usuario.md](./06-historias-usuario.md)).
2. Bajo cada User Story, crear **Tasks** según las tablas del doc [09-tareas-por-hu.md](./09-tareas-por-hu.md).
3. Las “Tareas transversales” del doc 09 (config proyecto, BD, auth, README) pueden ser una User Story tipo “Setup MVP” o tareas bajo la primera HU.

### Prioridad MVP estricto

Si quieres un MVP mínimo según la Definición del Proyecto (08), puedes **retrasar** en el orden:

- **HU-04** (autorización de visita) y **HU-13** (revocar autorización),  
y simplificar **HU-09** a “un usuario administrador y login simple”. El resto del orden se mantiene para poder desarrollar paso a paso y registrar las features de forma ordenada.

---

## 4. Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿El contexto está definido en la documentación? | Sí: toda la carpeta `docs/` (contexto, caso de negocio, requerimientos, arquitectura, modelo de datos, procesos, definición del proyecto, historias de usuario, tareas por HU, guía Git). |
| ¿Podemos iniciar desarrollo paso a paso en el orden de las HU y tareas? | Sí. Orden: setup → HU-05 → HU-01 → HU-03 → HU-04 (opcional MVP) → HU-06 → HU-07 → HU-09 → HU-02 → HU-08 → HU-10 → HU-11 → HU-13 → HU-14 → HU-12. |
| ¿Cómo registrar las features de forma ordenada? | Usar la tabla de la sección 2: una feature por fila, mismo orden para ramas Git y para User Stories/Tasks en Azure DevOps. |

---

**Documento**: Orden de desarrollo y registro de features  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
