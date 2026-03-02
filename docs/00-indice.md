# 📚 Índice de Documentación - SCA-EMPX

## Bienvenido a la Documentación del Sistema

Este índice te ayudará a navegar por toda la documentación del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** desarrollado para Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.).

---

## 📋 Documentos Disponibles

### 1. [Contexto Empresarial](./01-contexto-empresarial.md)
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

### 2. [Caso de Negocio](./02-caso-de-negocio.md)
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

### 3. [Definición del Proyecto](./08-definicion-proyecto.md)
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

### 4. [Requerimientos (SRS)](./03-requerimientos-srs.md)
**Descripción**: Especificación completa de requerimientos funcionales y no funcionales.

**Contenido**:
- Introducción y alcance
- Actores del sistema
- Requerimientos funcionales (RF-01 a RF-10)
- Requerimientos no funcionales (RNF-01 a RNF-07)
- Restricciones y dependencias

**Audiencia**: Desarrolladores, analistas, QA, arquitectos.

---

### 5. [Arquitectura del Sistema](./04-arquitectura.md)
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

### 6. [Modelo de Datos](./05-modelo-datos.md)
**Descripción**: Esquema completo de base de datos, tablas, relaciones y optimizaciones.

**Contenido**:
- Diagrama entidad-relación (descripción)
- Esquema de todas las tablas
- Relaciones entre tablas
- Índices y optimizaciones
- Scripts SQL de ejemplo

**Audiencia**: Desarrolladores, DBA, analistas de datos.

---

### 7. [Historias de Usuario](./06-historias-usuario.md)
**Descripción**: Backlog ágil con historias de usuario priorizadas y organizadas por épicas.

**Contenido**:
- 15+ historias de usuario detalladas
- Criterios de aceptación
- Priorización y estimación
- Backlog por sprints
- Definición de terminado

**Audiencia**: Product Owner, Scrum Master, equipo de desarrollo.

---

### 8. [Procesos BPMN](./07-procesos-bpmn.md)
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

### 9. [Tareas por HU](./09-tareas-por-hu.md)
**Descripción**: Tareas de desarrollo desglosadas por Historia de Usuario (para desarrollo y Azure DevOps).

**Contenido**:
- Desglose de tareas por cada historia de usuario
- Trazabilidad con requerimientos y cronograma
- Uso en backlog y planificación de sprints

**Audiencia**: Desarrolladores, Product Owner, Scrum Master.

---

### 10. [Guía de Uso de Git](./guia-git.md)
**Descripción**: Cómo usar Git en el proyecto SCA-EMPX: flujo diario, ramas, commits, sincronización con el remoto y buenas prácticas.

**Contenido**:
- Configuración inicial y clonado
- Flujo de trabajo (status, add, commit, push, pull)
- Ramas (crear, cambiar, convenciones)
- Deshacer cambios y sincronización con el remoto
- Integración con Azure DevOps y buenas prácticas

**Audiencia**: Desarrolladores, líder de proyecto, cualquier persona que contribuya al repositorio.

---

### 11. [Orden de desarrollo y registro de features](./orden-desarrollo-features.md)
**Descripción**: Confirmación del contexto según la documentación y orden recomendado para iniciar el desarrollo paso a paso y registrar features (ramas Git y backlog) de forma ordenada.

**Contenido**:
- Contexto del proyecto y MVP según docs 06, 08 y 09
- Tabla ordenada de features (HU + nombre de rama sugerido)
- Cómo usar el orden en Git y en Azure DevOps
- Prioridad MVP estricto

**Audiencia**: Desarrolladores, Product Owner, Scrum Master.

---

### 12. [URLs de acceso](./urls-acceso.md)
**Descripción**: Listado de URLs para acceder a la aplicación: páginas web, documentación de la API y endpoints REST.

**Contenido**:
- Páginas web (validate-access, registro empleado/visitante, autorización, registrar salida)
- Documentación OpenAPI (Swagger, ReDoc)
- API REST por recurso (personas, access, events, autorizaciones, usuarios)

**Audiencia**: Desarrolladores, QA, usuarios que prueben la API.

---

## 🗺️ Guía de Lectura Recomendada

### Para Nuevos Miembros del Equipo

1. **Contexto Empresarial** - Entender la empresa y el problema
2. **Caso de Negocio** - Entender por qué se hace el proyecto
3. **Definición del Proyecto** - Entender objetivos, alcance y cronograma
4. **Requerimientos (SRS)** - Entender qué se debe construir
5. **Arquitectura** - Entender cómo se construye
6. **Modelo de Datos** - Entender la estructura de datos
7. **Historias de Usuario** - Entender las funcionalidades
8. **Procesos BPMN** - Entender los flujos de negocio

### Para Desarrolladores

1. **Requerimientos (SRS)** - Qué construir
2. **Arquitectura** - Cómo construir
3. **Modelo de Datos** - Estructura de datos
4. **Historias de Usuario** - Funcionalidades a implementar
5. **Procesos BPMN** - Flujos a implementar

### Para Product Owner / Analistas

1. **Contexto Empresarial** - Contexto del negocio
2. **Caso de Negocio** - Justificación
3. **Requerimientos (SRS)** - Qué se necesita
4. **Historias de Usuario** - Qué desarrollar
5. **Procesos BPMN** - Cómo funciona el negocio

### Para Directivos / Stakeholders

1. **Contexto Empresarial** - Resumen ejecutivo
2. **Caso de Negocio** - Justificación y ROI
3. **Requerimientos (SRS)** - Resumen de funcionalidades

---

## 📊 Mapa de Relaciones entre Documentos

```
Contexto Empresarial
    ↓
Caso de Negocio
    ↓
Definición del Proyecto
    ↓
Requerimientos (SRS) ──→ Arquitectura ──→ Modelo de Datos
    ↓                           ↓
Historias de Usuario ──────────┘
    ↓
Procesos BPMN
```

---

## 🔍 Búsqueda Rápida

### ¿Necesitas información sobre...?

- **La empresa y el contexto**: [Contexto Empresarial](./01-contexto-empresarial.md)
- **Por qué hacer el proyecto**: [Caso de Negocio](./02-caso-de-negocio.md)
- **Objetivos y cronograma**: [Definición del Proyecto](./08-definicion-proyecto.md)
- **Qué funcionalidades tiene**: [Requerimientos (SRS)](./03-requerimientos-srs.md)
- **Cómo está diseñado**: [Arquitectura](./04-arquitectura.md)
- **Estructura de la base de datos**: [Modelo de Datos](./05-modelo-datos.md)
- **Qué desarrollar primero**: [Historias de Usuario](./06-historias-usuario.md)
- **Cómo funciona el proceso**: [Procesos BPMN](./07-procesos-bpmn.md)
- **Tareas de desarrollo por HU (para desarrollo y Azure DevOps)**: [Tareas por HU](./09-tareas-por-hu.md)
- **Orden para desarrollar y registrar features (ramas Git / backlog)**: [Orden desarrollo y features](./orden-desarrollo-features.md)
- **Bitácora de desarrollo (check de actividades, orden, avance)**: [Bitácora de desarrollo](./bitacora-desarrollo.md)
- **URLs para acceder a la API y páginas (listado completo)**: [URLs de acceso](./urls-acceso.md)
- **Uso de Git (ramas, commits, ambientes, pull, push)**: [Guía de Uso de Git](./guia-git.md)
- **Flujo MLOps (entrenamiento, registro, promoción, despliegue)**: [Flujo MLOps](./mlops-flujo.md)
- **Monitoreo del modelo en producción (métricas y dónde registrarlas)**: [Monitoreo en producción](./mlops-monitoreo-produccion.md)

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
