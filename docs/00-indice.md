# 📚 Índice de Documentación - SCA-EMPX

## Bienvenido

Este índice es el **punto de entrada** a la documentación del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** (STI S.A.S.). Está pensado para que un **desarrollador** o el **profesor** encuentren rápido qué leer según su rol.

**¿Primera vez en el proyecto?**  
- **Desarrollador:** [Requerimientos (SRS)](./03-requerimientos-srs.md) → [Arquitectura](./04-arquitectura.md) → [URLs de acceso](./urls-acceso.md) → [Guía Git](./guia-git.md).  
- **Profesor / evaluador:** [Plan y roadmap (Fases 0–5)](./plan-roadmap.md) → [Flujo MLOps](./mlops-flujo.md) → [Despliegue Docker](./despliegue-docker.md).  
- **Negocio / producto:** [Contexto Empresarial](./01-contexto-empresarial.md) → [Caso de Negocio](./02-caso-de-negocio.md) → [Historias de Usuario](./06-historias-usuario.md).

---

## 1. Negocio y proyecto

Documentos de contexto, justificación, alcance y especificación del sistema.

### 1.1 [Contexto Empresarial](./01-contexto-empresarial.md)
**Descripción**: Información sobre STI S.A.S., estructura organizacional, instalaciones y necesidad del sistema.

**Contenido**:
- Descripción general de la empresa
- Identidad corporativa (misión, visión, valores)
- Estructura organizacional
- Instalaciones físicas
- Tipos de personas que ingresan
- Necesidad del sistema de control de acceso

**Audiencia**: Stakeholders, equipo de proyecto, nuevos miembros del equipo.

---

### 1.2 [Caso de Negocio](./02-caso-de-negocio.md)
**Descripción**: Justificación de la inversión, beneficios esperados y análisis de ROI.

**Contenido**:
- Problema actual
- Objetivo de la solución
- Beneficios esperados (seguridad, cumplimiento, eficiencia)
- Riesgos de no implementar
- Análisis de inversión y ROI
- Métricas de éxito

**Audiencia**: Directivos, patrocinadores del proyecto, comité de aprobación.

---

### 1.3 [Definición del Proyecto](./08-definicion-proyecto.md)
**Descripción**: Documento estructurado con objetivos, alcance y cronograma del proyecto de desarrollo.

**Contenido**:
- Contexto del proyecto
- Objetivos y alcance (general y específicos)
- Cronograma detallado con tareas
- Diagrama de Gantt
- Recursos necesarios
- Riesgos y mitigaciones

**Audiencia**: Equipo de proyecto, directivos, estudiantes de desarrollo de proyectos de IA.

---

### 1.4 [Requerimientos (SRS)](./03-requerimientos-srs.md)
**Descripción**: Especificación completa de requerimientos funcionales y no funcionales.

**Contenido**:
- Introducción y alcance
- Actores del sistema
- Requerimientos funcionales (RF-01 a RF-10)
- Requerimientos no funcionales (RNF-01 a RNF-07)
- Restricciones y dependencias

**Audiencia**: Desarrolladores, analistas, QA, arquitectos.

---

### 1.5 [Arquitectura del Sistema](./04-arquitectura.md)
**Descripción**: Diseño arquitectónico, componentes y tecnologías del sistema.

**Contenido**:
- Principios arquitectónicos
- Arquitectura en capas
- Descripción de componentes
- Flujos de datos
- Consideraciones de despliegue
- Tecnologías sugeridas

**Audiencia**: Arquitectos, desarrolladores, DevOps.

---

### 1.6 [Modelo de Datos](./05-modelo-datos.md)
**Descripción**: Esquema completo de base de datos, tablas, relaciones y optimizaciones.

**Contenido**:
- Diagrama entidad-relación (descripción)
- Esquema de todas las tablas
- Relaciones entre tablas
- Índices y optimizaciones
- Scripts SQL de ejemplo

**Audiencia**: Desarrolladores, DBA, analistas de datos.

---

### 1.7 [Historias de Usuario](./06-historias-usuario.md)
**Descripción**: Backlog ágil con historias de usuario priorizadas y organizadas por épicas.

**Contenido**:
- 15+ historias de usuario detalladas
- Criterios de aceptación
- Priorización y estimación
- Backlog por sprints
- Definición de terminado

**Audiencia**: Product Owner, Scrum Master, equipo de desarrollo.

---

### 1.8 [Procesos BPMN](./07-procesos-bpmn.md)
**Descripción**: Flujos de negocio detallados en notación BPMN (descripción textual).

**Contenido**:
- Proceso de ingreso a la empresa (paso a paso)
- Proceso de salida de la empresa
- Proceso de registro de visitante
- Proceso de desactivación de empleado
- Reglas de negocio
- Manejo de excepciones

**Audiencia**: Analistas de negocio, desarrolladores, usuarios finales.

---

### 1.9 [Tareas por HU](./09-tareas-por-hu.md)
**Descripción**: Tareas de desarrollo desglosadas por Historia de Usuario (para desarrollo y Azure DevOps).

**Contenido**:
- Desglose de tareas por cada historia de usuario
- Trazabilidad con requerimientos y cronograma
- Uso en backlog y planificación de sprints

**Audiencia**: Desarrolladores, Product Owner, Scrum Master.

---

## 2. Desarrollo y operación

Orden de trabajo, bitácora, URLs de la aplicación y flujo con Git.

### 2.1 [Orden de desarrollo y registro de features](./orden-desarrollo-features.md)
**Descripción**: Orden recomendado para desarrollar y registrar features (ramas Git y backlog).

**Contenido**: Contexto según documentación, tabla de features (HU + rama sugerida), uso en Git y Azure DevOps.

**Audiencia**: Desarrolladores, Product Owner, Scrum Master.

---

### 2.2 [Bitácora de desarrollo](./bitacora-desarrollo.md)
**Descripción**: Estado de avance por feature (HUs) y por roadmap ML (Fases 0–5), checklist de actividades y trazabilidad.

**Audiencia**: Equipo de proyecto, profesor.

---

### 2.3 [URLs de acceso](./urls-acceso.md)
**Descripción**: Listado de URLs: páginas web, documentación de la API y endpoints REST.

**Contenido**: Páginas (/, /registro, /acceso, /visitante, /configuracion), Swagger/ReDoc, API por recurso (personas, acceso, eventos, autorizaciones, usuarios).

**Audiencia**: Desarrolladores, QA.

---

### 2.4 [Guía de Uso de Git](./guia-git.md)
**Descripción**: Cómo usar Git en el proyecto SCA-EMPX: flujo diario, ramas, commits, sincronización con el remoto y buenas prácticas.

**Contenido**:
- Configuración inicial y clonado
- Flujo de trabajo (status, add, commit, push, pull)
- Ramas (crear, cambiar, convenciones)
- Deshacer cambios y sincronización con el remoto
- Integración con Azure DevOps y buenas prácticas

**Audiencia**: Desarrolladores, líder de proyecto, cualquier persona que contribuya al repositorio.

---

## 3. MLOps y pipeline de monitoreo

Plan del roadmap ML (Fases 0–5), flujo de entrenamiento/registro/promoción, monitoreo en producción y despliegue con Docker.

### 3.1 [Plan y roadmap general](./plan-roadmap.md)
**Descripción**: Plan del proyecto: contexto, estrategia de ramas, orden de fases (0 → 5), detalle de cada fase (modelos, MLFlow, Comet, MLOps, Docker, pipeline) y cumplimiento de la Guía de Monitoreo ML-IA.

**Contenido**: Cómo usar el documento, orden Fase 0–5, anexos con tareas por fase y checklist de entrega.

**Audiencia**: Profesor, desarrolladores, equipo de proyecto.

---

### 3.2 [Flujo MLOps](./mlops-flujo.md)
**Descripción**: Flujo completo: entrenamiento → registro (MLFlow/Comet) → criterios de promoción → despliegue.

**Audiencia**: Desarrolladores, DevOps, profesor.

---

### 3.3 [Monitoreo en producción](./mlops-monitoreo-produccion.md)
**Descripción**: Métricas a monitorear en producción (latencia, errores, distribución de scores) y dónde registrarlas.

**Audiencia**: Desarrolladores, DevOps.

---

### 3.4 [Despliegue con Docker](./despliegue-docker.md)
**Descripción**: Arquitectura del despliegue, build, `docker compose up`, variables de entorno, ejecución del entrenamiento en Docker (API, MLFlow, servicio train).

**Audiencia**: Desarrolladores, DevOps, profesor.

---

## 4. Guías de uso

### 4.1 [Guía de uso de la aplicación](./guia-uso-aplicacion.md)
**Descripción**: Cómo usar SCA-EMPX desde el navegador: instalación, menú, pantallas (registro, acceso, visitante, etc.) y flujos principales.

**Audiencia**: Usuarios finales, QA, desarrolladores que prueban la UI.

---

## 🗺️ Guía de lectura recomendada

### Para profesor / evaluador

1. [Plan y roadmap](./plan-roadmap.md) — Fases 0–5, entregables y Guía ML-IA  
2. [Flujo MLOps](./mlops-flujo.md) — Entrenamiento, registro, promoción, despliegue  
3. [Despliegue Docker](./despliegue-docker.md) — Cómo se ejecuta todo en contenedores  
4. [Bitácora de desarrollo](./bitacora-desarrollo.md) — Estado de avance por feature  

### Para desarrollador (nuevo en el proyecto)

1. [Requerimientos (SRS)](./03-requerimientos-srs.md) — Qué construir  
2. [Arquitectura](./04-arquitectura.md) — Cómo está diseñado  
3. [Modelo de Datos](./05-modelo-datos.md) — Estructura de datos  
4. [URLs de acceso](./urls-acceso.md) — Páginas y API  
5. [Guía de Git](./guia-git.md) — Ramas, commits, flujo  
6. [Orden desarrollo y features](./orden-desarrollo-features.md) — Qué desarrollar y en qué orden  

### Para negocio / producto

1. [Contexto Empresarial](./01-contexto-empresarial.md) — Empresa y necesidad  
2. [Caso de Negocio](./02-caso-de-negocio.md) — Justificación y ROI  
3. [Requerimientos (SRS)](./03-requerimientos-srs.md) — Funcionalidades  
4. [Historias de Usuario](./06-historias-usuario.md) — Backlog  
5. [Procesos BPMN](./07-procesos-bpmn.md) — Flujos de negocio  

### Para usuario que prueba la aplicación

1. [Guía de uso de la aplicación](./guia-uso-aplicacion.md) — Pantallas y flujos desde el navegador

---

## 📊 Mapa de relaciones entre documentos

```
Negocio y proyecto:
  Contexto Empresarial → Caso de Negocio → Definición del Proyecto
  Requerimientos (SRS) → Arquitectura → Modelo de Datos
  Historias de Usuario → Procesos BPMN → Tareas por HU

Desarrollo y operación:
  Orden desarrollo y features → Bitácora → URLs de acceso → Guía Git

MLOps y pipeline:
  Plan y roadmap (Fases 0–5) → Flujo MLOps → Monitoreo producción → Despliegue Docker
```

---

## 🔍 Búsqueda rápida

**Negocio y proyecto:** [Contexto](./01-contexto-empresarial.md) · [Caso de negocio](./02-caso-de-negocio.md) · [Definición](./08-definicion-proyecto.md) · [Requerimientos](./03-requerimientos-srs.md) · [Arquitectura](./04-arquitectura.md) · [Modelo de datos](./05-modelo-datos.md) · [Historias de usuario](./06-historias-usuario.md) · [BPMN](./07-procesos-bpmn.md) · [Tareas por HU](./09-tareas-por-hu.md)

**Desarrollo y operación:** [Orden y features](./orden-desarrollo-features.md) · [Bitácora](./bitacora-desarrollo.md) · [URLs de acceso](./urls-acceso.md) · [Guía Git](./guia-git.md)

**MLOps y pipeline:** [Plan y roadmap](./plan-roadmap.md) · [Flujo MLOps](./mlops-flujo.md) · [Monitoreo en producción](./mlops-monitoreo-produccion.md) · [Despliegue Docker](./despliegue-docker.md)

**Guías:** [Uso de la aplicación](./guia-uso-aplicacion.md)

---

## 📝 Convenciones de la Documentación

- **Versión**: Todos los documentos están en versión 1.0
- **Formato**: Markdown (.md)
- **Fecha**: 2026
- **Autor**: Equipo de Proyecto STI S.A.S.

---

## 🔄 Actualizaciones

Esta documentación se actualizará según el avance del proyecto. Cada documento incluye su versión y fecha de última actualización.

---

## 📞 Contacto

Para preguntas o sugerencias sobre la documentación, contactar al equipo de proyecto.

---

**Documento**: Índice de Documentación  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
