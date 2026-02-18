# Guía de uso de la aplicación - SCA-EMPX

Esta guía describe cómo usar el **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** desde el navegador y, en su caso, desde la API.

**Requisito:** La API debe estar en ejecución en **http://127.0.0.1:8000** (o la URL configurada). Para arrancarla, ver [Instalación y ejecución](#1-instalación-y-ejecución) más abajo.

---

## 1. Instalación y ejecución

1. **Requisitos:** Python 3.13+, [uv](https://docs.astral.sh/uv/) (o pip).

2. **Instalar dependencias** (desde la raíz del proyecto):
   ```bash
   uv sync
   ```

3. **Inicializar la base de datos** (solo la primera vez):
   ```bash
   uv run python scripts/init_db.py
   ```
   Se crean las tablas y un usuario **admin** con contraseña **admin** (cambiar en producción).

4. **Arrancar la aplicación**:
   ```bash
   uv run python main.py
   ```
   O bien:
   ```bash
   uv run uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
   ```

5. Abrir en el navegador: **http://127.0.0.1:8000**

---

## 2. Resumen de pantallas (URLs)

| Pantalla | URL | Uso principal |
|----------|-----|----------------|
| Validar acceso (entrada) | http://127.0.0.1:8000/validate-access | Reconocimiento facial para permitir/denegar entrada |
| Registrar empleado | http://127.0.0.1:8000/registro-empleado | Alta de empleado con foto |
| Registrar visitante | http://127.0.0.1:8000/registro-visitante | Alta de visitante con foto y datos de visita |
| Autorización de visita | http://127.0.0.1:8000/autorizacion-visita | Crear autorización vigente para un visitante |
| Registrar salida | http://127.0.0.1:8000/registrar-salida | Reconocimiento facial para registrar salida |
| Listado de personas | http://127.0.0.1:8000/listado-personas | Buscar personas, Desactivar/Activar, enlace Editar |
| Editar persona | http://127.0.0.1:8000/editar-persona?id=**ID** | Editar nombre, cargo, área, teléfono, email, estado |
| Historial de accesos | http://127.0.0.1:8000/historial-accesos | Consultar eventos con filtros y exportar CSV |
| Dashboard | http://127.0.0.1:8000/dashboard | Métricas y últimos eventos (se actualiza cada 30 s) |
| Revocar autorización | http://127.0.0.1:8000/revocar-autorizacion | Listar autorizaciones vigentes y revocarlas |
| Personas dentro | http://127.0.0.1:8000/personas-dentro | Lista de personas que están dentro (sin salida registrada) |
| Reporte de accesos | http://127.0.0.1:8000/reporte-accesos | Descargar reporte por fechas en CSV o PDF |
| Administración de usuarios | http://127.0.0.1:8000/administracion-usuarios | Login, listado de usuarios, alta y activar/desactivar |

---

## 3. Uso por flujo

### 3.1 Validar acceso (entrada)

- **URL:** http://127.0.0.1:8000/validate-access  
- **Qué hace:** Permite subir una foto (o usar cámara si está disponible). El sistema intenta identificar el rostro con las personas activas registradas. Si hay coincidencia y la persona está activa, se **permite el acceso** y se registra un evento de **ingreso**. Si no, se **deniega** y se registra el intento.
- **Pasos:** Elegir/capturar imagen → Enviar → Ver resultado (permitido/denegado y motivo).

### 3.2 Registrar empleado

- **URL:** http://127.0.0.1:8000/registro-empleado  
- **Qué hace:** Alta de una persona como empleado con foto para reconocimiento facial.
- **Pasos:** Completar nombre, documento, cargo, área (opcionales), subir **foto con un rostro visible** → Enviar. El sistema genera el embedding facial. Si el documento ya existe, se muestra error.

### 3.3 Registrar visitante

- **URL:** http://127.0.0.1:8000/registro-visitante  
- **Qué hace:** Alta de un visitante con foto, empresa, motivo de visita y opcionalmente empleado visitado.
- **Pasos:** Completar nombre, documento, **empresa**, **motivo de visita**, subir foto → Enviar. Luego se puede crear una **autorización de visita** para que pueda ingresar en un rango de fechas.

### 3.4 Autorización de visita

- **URL:** http://127.0.0.1:8000/autorizacion-visita  
- **Qué hace:** Crea una autorización **vigente** para un visitante entre fecha inicio y fecha fin.
- **Pasos:** Seleccionar persona (visitante), fecha inicio y fecha fin → Crear. La autorización debe estar vigente para que la validación de acceso permita el ingreso del visitante (según reglas del negocio).

### 3.5 Registrar salida

- **URL:** http://127.0.0.1:8000/registrar-salida  
- **Qué hace:** Registra la **salida** de una persona identificada por reconocimiento facial.
- **Pasos:** Subir/capturar imagen → Enviar. El sistema identifica a la persona y registra el evento de salida.

### 3.6 Listado de personas

- **URL:** http://127.0.0.1:8000/listado-personas  
- **Qué hace:** Lista empleados y/o visitantes con búsqueda por nombre o documento y filtros por tipo y estado.
- **Acciones:**
  - **Desactivar / Activar:** cambia el estado de la persona (las inactivas no pueden validar acceso).
  - **Editar:** abre la pantalla de edición con `?id=<id_persona>`.

### 3.7 Editar persona

- **URL:** http://127.0.0.1:8000/editar-persona?id=**&lt;id&gt;**  
- **Qué hace:** Permite modificar nombre completo, cargo, área, teléfono, email y estado. El documento no se puede cambiar.
- **Pasos:** Abrir desde el listado (enlace Editar) o poniendo el ID en la URL → Modificar campos → Guardar cambios.

### 3.8 Historial de accesos

- **URL:** http://127.0.0.1:8000/historial-accesos  
- **Qué hace:** Muestra eventos de acceso (ingresos/salidas) con filtros: ID persona, documento, rango de fechas, tipo (ingreso/salida), resultado (permitido/denegado).
- **Acciones:** Ajustar filtros → Buscar. **Exportar CSV:** descarga los mismos datos filtrados en CSV (hasta 1000 filas por defecto en la descarga).

### 3.9 Dashboard

- **URL:** http://127.0.0.1:8000/dashboard  
- **Qué hace:** Muestra en tiempo (casi) real:
  - **Personas dentro:** cantidad de personas cuyo último evento es un ingreso permitido.
  - **Accesos hoy:** cantidad de eventos permitidos desde medianoche (UTC).
  - **Denegaciones hoy:** cantidad de eventos denegados desde medianoche (UTC).
  - Tabla de **últimos eventos** (últimos 10 minutos).
- La página se actualiza automáticamente cada 30 segundos.

### 3.10 Revocar autorización

- **URL:** http://127.0.0.1:8000/revocar-autorizacion  
- **Qué hace:** Lista autorizaciones (por defecto solo **vigentes**). Permite revocar una vigente con motivo opcional.
- **Pasos:** Seleccionar “Solo vigentes” (o otro filtro) → Actualizar → En la fila deseada, **Revocar** → Opcionalmente indicar motivo.

### 3.11 Personas dentro

- **URL:** http://127.0.0.1:8000/personas-dentro  
- **Qué hace:** Lista las personas que están “dentro” (último evento = ingreso permitido, sin salida posterior), con nombre y hora de entrada.
- La lista se actualiza cada 60 segundos.

### 3.12 Reporte de accesos

- **URL:** http://127.0.0.1:8000/reporte-accesos  
- **Qué hace:** Genera un reporte de eventos de acceso en un rango de fechas y lo descarga en **CSV** o **PDF**.
- **Pasos:** Elegir **Desde** y **Hasta** (fechas), **Formato** (CSV o PDF) → **Descargar reporte**. Se abre una nueva pestaña con el archivo; si no se descarga, revisar si el navegador bloquea descargas o la pestaña.

### 3.13 Administración de usuarios

- **URL:** http://127.0.0.1:8000/administracion-usuarios  
- **Qué hace:** Pantalla para gestionar usuarios del sistema: **login**, listado de usuarios, **alta** de usuarios (por ejemplo solo admin) y **activar/desactivar**.
- **Login:** usuario y contraseña (por defecto admin/admin tras `init_db.py`). El token se usa para llamadas API protegidas.
- **Alta de usuario:** nombre de usuario, contraseña y rol.  
- **Activar/Desactivar:** por usuario en el listado.

---

## 4. Documentación de la API

- **Swagger (OpenAPI):** http://127.0.0.1:8000/docs  
- **ReDoc:** http://127.0.0.1:8000/redoc (si está habilitado)

Desde ahí se pueden probar todos los endpoints (personas, acceso, eventos, autorizaciones, reportes, usuarios) y ver parámetros y respuestas.

Para más detalle de cada URL y query params, ver **[URLs de acceso](./urls-acceso.md)**.

---

## 5. Notas rápidas

- **Fechas:** En backend muchas fechas se manejan en UTC (dashboard “hoy”, eventos recientes, etc.).
- **Reconocimiento facial:** Se usa una sola foto por persona; la foto debe tener **un rostro bien visible**. Empleados y visitantes comparten el mismo flujo de registro con foto.
- **Personas inactivas:** No pueden validar acceso (entrada); desactivar desde el listado de personas.
- **Autorizaciones:** Solo se puede revocar una autorización en estado **vigente**; al revocar pasa a **revocada** y se puede guardar un motivo.

---

**Documento:** Guía de uso de la aplicación  
**Proyecto:** SCA-EMPX – STI S.A.S.  
**Versión:** 1.0
