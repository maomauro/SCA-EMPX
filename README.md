# 🏢 Sistema de Control de Acceso Físico - STI S.A.S.

## 📋 Descripción General

Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX) desarrollado para **Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.)**, una compañía colombiana dedicada al diseño, desarrollo e implementación de soluciones tecnológicas.

Este sistema permite gestionar el acceso físico a las instalaciones de la empresa, garantizando que solo personas registradas, autorizadas y en estado activo puedan ingresar, registrando además todas las entradas y salidas con trazabilidad completa.

## 🎯 Objetivos del Sistema

- ✅ Control estricto de quién entra y sale de las instalaciones
- ✅ **Reconocimiento facial como método principal** (ArcFace + YOLOv8)
- ✅ Registro de visitantes con trazabilidad completa
- ✅ Validación automática de autorizaciones
- ✅ Integración con cámaras y torniquetes automáticos
- ✅ Auditoría completa para incidentes de seguridad

## 📚 Documentación

La documentación completa del proyecto se encuentra en la carpeta [`docs/`](./docs/):

- **[📑 Índice de Documentación](./docs/00-indice.md)** - Guía de navegación y mapa de documentos
- **[🏢 Contexto Empresarial](./docs/01-contexto-empresarial.md)** - Información sobre STI S.A.S. y el contexto del proyecto
- **[💼 Caso de Negocio](./docs/02-caso-de-negocio.md)** - Justificación y beneficios de la inversión
- **[📊 Definición del Proyecto](./docs/08-definicion-proyecto.md)** - Objetivos, alcance y cronograma del proyecto
- **[📋 Requerimientos (SRS)](./docs/03-requerimientos-srs.md)** - Especificación completa de requerimientos funcionales y no funcionales
- **[🏗️ Arquitectura del Sistema](./docs/04-arquitectura.md)** - Diseño arquitectónico y componentes
- **[🗄️ Modelo de Datos](./docs/05-modelo-datos.md)** - Esquema de base de datos y relaciones
- **[👥 Historias de Usuario](./docs/06-historias-usuario.md)** - Backlog ágil con historias de usuario
- **[🔄 Procesos BPMN](./docs/07-procesos-bpmn.md)** - Flujos de negocio de ingreso y salida
- **[📋 Tareas por HU](./docs/09-tareas-por-hu.md)** - Tareas de desarrollo por historia de usuario
- **[📌 Orden desarrollo y features](./docs/orden-desarrollo-features.md)** - Orden para desarrollar y registrar features (Git / backlog)
- **[📘 Guía de Uso de Git](./docs/guia-git.md)** - Flujo de trabajo con Git (ramas, ambientes, commits, sincronización)

**💡 Recomendación**: Comienza por el [Índice de Documentación](./docs/00-indice.md) para una guía completa de lectura.

## 🏗️ Estructura del Proyecto

### Estructura actual (raíz del repositorio)

```
SCA-EMPX/
├── docs/                              # Documentación del proyecto
│   ├── 00-indice.md                   # Índice y guía de navegación
│   ├── 01-contexto-empresarial.md
│   ├── 02-caso-de-negocio.md
│   ├── 03-requerimientos-srs.md
│   ├── 04-arquitectura.md
│   ├── 05-modelo-datos.md
│   ├── 06-historias-usuario.md
│   ├── 07-procesos-bpmn.md
│   ├── 08-definicion-proyecto.md      # Objetivos, alcance, cronograma MVP
│   ├── 09-tareas-por-hu.md            # Tareas de desarrollo por HU
│   ├── orden-desarrollo-features.md   # Orden para desarrollar y registrar features
│   └── guia-git.md                    # Guía de uso de Git y ambientes
├── main.py                            # Punto de entrada de la aplicación (MVP)
├── pyproject.toml                     # Configuración del proyecto Python (uv/pip)
├── .python-version                    # Versión de Python del proyecto
├── .gitignore
├── uv.lock                            # Lockfile de dependencias (uv)
└── README.md
```

*El entorno virtual (`.venv/`) se genera localmente y no se versiona.*

### Estructura prevista al avanzar el desarrollo (referencia: [04-arquitectura.md](./docs/04-arquitectura.md))

Cuando se implemente el MVP según las [tareas por HU](./docs/09-tareas-por-hu.md), la estructura podría evolucionar así:

```
SCA-EMPX/
├── docs/                    # (igual que arriba)
├── backend/                 # API y lógica de negocio (FastAPI/Flask)
│   ├── app/
│   │   ├── api/             # Endpoints REST
│   │   ├── core/            # Config, seguridad, BD
│   │   ├── models/          # Modelos de datos
│   │   ├── services/        # Lógica de negocio y reconocimiento facial
│   │   └── main.py
│   ├── tests/
│   └── requirements.txt o pyproject.toml
├── frontend/                 # Interfaz web (React o HTML/JS simple)
│   ├── src/
│   └── ...
├── scripts/                  # Scripts de utilidad (ej. convertir docs a Word)
├── main.py                   # Punto de entrada o redirección
├── pyproject.toml
└── README.md
```

La estructura definitiva se ajustará según las decisiones del equipo y el documento [Arquitectura del Sistema](./docs/04-arquitectura.md).

## 👥 Actores del Sistema

- **Empleado**: Persona de planta o contratista con acceso recurrente
- **Visitante**: Persona externa que ingresa por una visita específica
- **Recepcionista**: Registra visitantes y gestiona autorizaciones puntuales
- **Administrador de Seguridad**: Configura reglas, consulta auditoría, gestiona accesos
- **RRHH**: Gestiona altas/bajas de empleados
- **Sistema de Torniquetes/Control Físico**: Dispositivo que valida acceso

## 🚀 Estado del Proyecto

**Fase Actual**: Documentación y diseño

Este repositorio contiene la documentación completa del proyecto. La implementación técnica se desarrollará en fases posteriores.

## 📝 Licencia

Documentación interna de STI S.A.S. - Uso confidencial.

---

**Desarrollado para**: Soluciones Tecnológicas Integrales S.A.S.  
**Ubicación**: Bogotá, Colombia  
**Año**: 2026
