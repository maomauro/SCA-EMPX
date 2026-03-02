# Guía de uso de la aplicación - SCA-EMPX

Esta guía describe cómo usar el **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** desde el navegador y, en su caso, desde la API.

**Requisito:** La API debe estar en ejecución en **http://127.0.0.1:8000** (o la URL configurada). Para arrancarla, ver [Instalación y ejecución](#1-instalación-y-ejecución) más abajo. Documentación general del proyecto: [README.md](../README.md) y [Índice de documentación](./00-indice.md).

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

5. Abrir en el navegador: **http://127.0.0.1:8000/** (página principal/dashboard). Health check: **http://127.0.0.1:8000/health** (JSON).

---

## 2. Menú de navegación e inicio

Todas las pantallas de la aplicación incluyen una **barra de navegación** superior (fondo azul oscuro) con enlaces a:

- **Inicio** – Página principal con tarjetas por módulo  
- **Validar acceso**, **Reg. empleado**, **Reg. visitante**, **Autorización**, **Reg. salida**  
- **Personas** (listado), **Historial**, **Dashboard**, **Revocar auth.**, **Personas dentro**, **Reporte**, **Admin**

Desde cualquier página se puede cambiar de pantalla sin escribir URLs. La **página principal** (`/`) actúa como inicio; según la implementación puede incluir menú y enlaces a los módulos (acceso, registro, visitante, configuración).

---

## 3. Resumen de pantallas (URLs)

**Listado oficial de URLs:** [urls-acceso.md](./urls-acceso.md).

| Pantalla | URL | Uso principal |
|----------|-----|----------------|
| **Página principal** | http://127.0.0.1:8000/ | Inicio y navegación |
| **Registro** | http://127.0.0.1:8000/registro | Alta de persona con captura facial |
| **Validar acceso (entrada/salida)** | http://127.0.0.1:8000/acceso | Reconocimiento facial, registrar entrada o salida |
| **Visitante / autorización** | http://127.0.0.1:8000/visitante | Registro de visitante y autorización de visita |
| **Configuración** | http://127.0.0.1:8000/configuracion | Configuración del sistema |
| **Documentación API** | http://127.0.0.1:8000/docs | Swagger UI (OpenAPI) |

Otras pantallas (listado personas, historial, dashboard, reportes, administración de usuarios) pueden estar en otras rutas o pendientes; ver [URLs de acceso](./urls-acceso.md) y [Bitácora de desarrollo](./bitacora-desarrollo.md).

---

## 4. Uso por flujo

### 4.1 Validar acceso (entrada/salida)

- **URL:** http://127.0.0.1:8000/acceso  
- **Qué hace:** Permite subir una foto (o usar cámara si está disponible). El sistema intenta identificar el rostro con las personas activas registradas. Si hay coincidencia y la persona está autorizada, se **permite el acceso** y se registra un evento de **ingreso** o **salida**. Si no, se **deniega** y se registra el intento.
- **Pasos:** Elegir/capturar imagen → Enviar → Ver resultado (permitido/denegado y motivo).

### 4.2 Registrar persona (empleado o visitante)

- **URL:** http://127.0.0.1:8000/registro  
- **Qué hace:** Alta de una persona (empleado o visitante) con foto para reconocimiento facial.
- **Pasos:** Completar datos (nombre, documento, tipo de persona, cargo/área si aplica), subir **foto con un rostro visible** → Enviar. El sistema genera el embedding facial. Si el documento ya existe, se puede mostrar error según implementación.

### 4.3 Visitante y autorización de visita

- **URL:** http://127.0.0.1:8000/visitante  
- **Qué hace:** Registro de visitante y creación de **autorización de visita** (vigente entre fecha inicio y fecha fin) para que pueda ingresar en ese rango.
- **Pasos:** Completar datos del visitante y/o seleccionar persona (visitante), fecha inicio y fecha fin → Crear autorización. La autorización vigente es tenida en cuenta en la validación de acceso.

### 4.4 Configuración

- **URL:** http://127.0.0.1:8000/configuracion  
- **Qué hace:** Configuración del sistema (umbrales, parámetros, etc., según implementación).

### 4.5 Registrar salida (desde pantalla de acceso)

- **URL:** http://127.0.0.1:8000/acceso (misma pantalla que validar entrada).  
- **Qué hace:** Registra la **salida** de una persona identificada por reconocimiento facial.
- **Pasos:** Subir/capturar imagen → Enviar. El sistema identifica a la persona y registra el evento de salida.

### 4.6 Listado de personas

Las siguientes pantallas (4.6 en adelante) pueden estar en rutas propias o integradas en las páginas actuales; ver [URLs de acceso](./urls-acceso.md) y [bitácora](./bitacora-desarrollo.md).

- **URL:** http://127.0.0.1:8000/listado-personas  
- **Qué hace:** Lista empleados y/o visitantes con búsqueda por nombre o documento y filtros por tipo y estado.
- **Acciones:**
  - **Desactivar / Activar:** cambia el estado de la persona (las inactivas no pueden validar acceso).
  - **Editar:** abre la pantalla de edición con `?id=<id_persona>`.

### 4.7 Editar persona

- **URL:** http://127.0.0.1:8000/editar-persona?id=**&lt;id&gt;**  
- **Qué hace:** Permite modificar nombre completo, cargo, área, teléfono, email y estado. El documento no se puede cambiar.
- **Pasos:** Abrir desde el listado (enlace Editar) o poniendo el ID en la URL → Modificar campos → Guardar cambios.

### 4.8 Historial de accesos

- **URL:** http://127.0.0.1:8000/historial-accesos  
- **Qué hace:** Muestra eventos de acceso (ingresos/salidas) con filtros: ID persona, documento, rango de fechas, tipo (ingreso/salida), resultado (permitido/denegado).
- **Acciones:** Ajustar filtros → Buscar. **Exportar CSV:** descarga los mismos datos filtrados en CSV (hasta 1000 filas por defecto en la descarga).

### 4.9 Dashboard

- **URL:** http://127.0.0.1:8000/dashboard  
- **Qué hace:** Muestra en tiempo (casi) real:
  - **Personas dentro:** cantidad de personas cuyo último evento es un ingreso permitido.
  - **Accesos hoy:** cantidad de eventos permitidos desde medianoche (UTC).
  - **Denegaciones hoy:** cantidad de eventos denegados desde medianoche (UTC).
  - Tabla de **últimos eventos** (últimos 10 minutos).
- La página se actualiza automáticamente cada 30 segundos.

### 4.10 Revocar autorización

- **URL:** http://127.0.0.1:8000/revocar-autorizacion  
- **Qué hace:** Lista autorizaciones (por defecto solo **vigentes**). Permite revocar una vigente con motivo opcional.
- **Pasos:** Seleccionar “Solo vigentes” (o otro filtro) → Actualizar → En la fila deseada, **Revocar** → Opcionalmente indicar motivo.

### 4.11 Personas dentro

- **URL:** http://127.0.0.1:8000/personas-dentro  
- **Qué hace:** Lista las personas que están “dentro” (último evento = ingreso permitido, sin salida posterior), con nombre y hora de entrada.
- La lista se actualiza cada 60 segundos.

### 4.12 Reporte de accesos

- **URL:** http://127.0.0.1:8000/reporte-accesos  
- **Qué hace:** Genera un reporte de eventos de acceso en un rango de fechas y lo descarga en **CSV** o **PDF**.
- **Pasos:** Elegir **Desde** y **Hasta** (fechas), **Formato** (CSV o PDF) → **Descargar reporte**. Se abre una nueva pestaña con el archivo; si no se descarga, revisar si el navegador bloquea descargas o la pestaña.

### 4.13 Administración de usuarios

- **URL:** http://127.0.0.1:8000/administracion-usuarios  
- **Qué hace:** Pantalla para gestionar usuarios del sistema: **login**, listado de usuarios, **alta** de usuarios (por ejemplo solo admin) y **activar/desactivar**.
- **Login:** usuario y contraseña (por defecto admin/admin tras `init_db.py`). El token se usa para llamadas API protegidas.
- **Alta de usuario:** nombre de usuario, contraseña y rol.  
- **Activar/Desactivar:** por usuario en el listado.

---

## 5. Documentación de la API

- **Swagger (OpenAPI):** http://127.0.0.1:8000/docs  
- **ReDoc:** http://127.0.0.1:8000/redoc (si está habilitado)

Desde ahí se pueden probar todos los endpoints (personas, acceso, eventos, autorizaciones, reportes, usuarios) y ver parámetros y respuestas.

Para más detalle de cada URL y query params, ver **[URLs de acceso](./urls-acceso.md)**.

---

## 6. Notas rápidas

- **Fechas:** En backend muchas fechas se manejan en UTC (dashboard “hoy”, eventos recientes, etc.).
- **Reconocimiento facial:** Se usa una sola foto por persona; la foto debe tener **un rostro bien visible**. Empleados y visitantes comparten el mismo flujo de registro con foto.
- **Personas inactivas:** No pueden validar acceso (entrada); desactivar desde el listado de personas.
- **Autorizaciones:** Solo se puede revocar una autorización en estado **vigente**; al revocar pasa a **revocada** y se puede guardar un motivo.

---

**Documento:** Guía de uso de la aplicación  
**Proyecto:** SCA-EMPX – STI S.A.S.  
**Versión:** 1.0
