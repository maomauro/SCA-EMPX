# 📋 Definición del Proyecto - MVP
## Sistema de Control de Acceso Físico con Reconocimiento Facial (SCA-EMPX)

**Proyecto:** Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas - MVP  
**Cliente:** Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.)  
**Fecha de Elaboración:** 2026  
**Versión:** MVP 1.0  
**Duración:** 3 semanas

---

## 1. Contexto del Proyecto

### 1.1. Contexto Empresarial

**Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.)** es una compañía colombiana con sede en Bogotá, dedicada al diseño, desarrollo e implementación de soluciones tecnológicas para sectores estratégicos como banca, retail, logística y gobierno. La empresa se caracteriza por su enfoque en la innovación, seguridad de la información y automatización de procesos críticos.

La organización cuenta con:
- Oficinas administrativas
- Centro de desarrollo de software
- Data center interno
- Zonas restringidas con acceso controlado

### 1.2. Necesidad del Proyecto

Actualmente, STI S.A.S. enfrenta limitaciones significativas en el control de acceso físico a sus instalaciones:

#### Problemas Identificados:
1. **Falta de Control Centralizado**: No existe un sistema centralizado que gestione quién entra y sale de las instalaciones. Los registros se realizan de forma manual (papel, Excel) o no se realizan.

2. **Gestión Manual de Visitantes**: Los visitantes pueden ingresar sin registro formal o con registros manuales poco confiables, dificultando la validación de autorizaciones en tiempo real.

3. **Ausencia de Trazabilidad Confiable**: No hay registro confiable para auditorías de seguridad, imposibilitando responder rápidamente a preguntas como "¿Quién estuvo en la empresa el día X a las Y horas?".

4. **Falta de Control de Accesos**: No hay control automatizado de quién ingresa y sale de la empresa, dificultando la restricción de accesos temporales.

5. **Dificultad para Responder a Incidentes**: Ante un incidente de seguridad, no hay evidencia confiable de accesos, requiriendo tiempo excesivo para investigaciones.

### 1.3. Justificación Tecnológica

El proyecto se fundamenta en el uso de **Inteligencia Artificial (IA)** para el reconocimiento facial. Para el MVP, se utilizarán **librerías pre-entrenadas** que permiten implementar reconocimiento facial de forma rápida y eficiente:

- **Librerías Pre-entrenadas**: Se utilizarán librerías como `face_recognition`, `DeepFace` o `MediaPipe` que incluyen modelos de deep learning ya entrenados para:
  - Detección de rostros en imágenes
  - Generación de embeddings faciales (vectores de características)
  - Comparación de embeddings para identificación
- **Métricas de Similaridad**: Uso de distancia euclidiana o similitud coseno para comparar embeddings y determinar identidad

**Nota para futuras iteraciones**: En versiones posteriores del sistema se podría considerar el uso de modelos más avanzados como YOLOv8 para detección y ArcFace para embeddings, pero para el MVP se prioriza la rapidez de implementación usando librerías pre-entrenadas.

Esta tecnología permite:
- Identificación automática sin necesidad de tarjetas o credenciales físicas
- Validación en tiempo aceptable (< 10 segundos para MVP)
- Precisión adecuada para demostración del concepto
- Experiencia de usuario fluida y no invasiva

### 1.4. Enfoque MVP (Producto Mínimo Viable)

Este proyecto se desarrollará como un **MVP (Producto Mínimo Viable)** con un alcance reducido que permita:
- Validar la viabilidad técnica del reconocimiento facial
- Demostrar el concepto básico de funcionamiento
- Obtener retroalimentación temprana de usuarios
- Establecer la base para futuras iteraciones

**Duración del MVP:** 3 semanas  
**Objetivo:** Entregar un sistema funcional básico que demuestre el concepto de reconocimiento facial para control de acceso.

---

## 2. Objetivos y Alcance - MVP

### 2.1. Objetivo General del MVP

Desarrollar un prototipo funcional de sistema de control de acceso basado en reconocimiento facial que permita:
- Registrar personas con foto facial
- Identificar personas mediante reconocimiento facial
- Validar acceso básico
- Registrar eventos de ingreso/salida

**Nota:** Este MVP se enfoca en demostrar la viabilidad técnica y obtener retroalimentación, no en una solución completa de producción.

### 2.2. Objetivos Específicos del MVP

#### 2.2.1. Objetivos Funcionales Mínimos

1. **Sistema de Reconocimiento Facial Básico**
   - Integrar modelo pre-entrenado de reconocimiento facial (Face Recognition o similar)
   - Detectar rostros en imágenes
   - Generar embeddings faciales básicos
   - Comparar embeddings para identificar personas
   - Tiempo de respuesta aceptable (< 10 segundos para MVP)

2. **Registro Básico de Personas**
   - Interfaz web simple para registrar personas
   - Captura de foto facial desde webcam o archivo
   - Almacenamiento de información básica (nombre, documento, tipo)
   - Almacenamiento de embedding facial
   - Estado activo/inactivo básico

3. **Validación de Acceso Básica**
   - Endpoint API para validar acceso mediante foto
   - Comparación de foto recibida con embeddings almacenados
   - Respuesta de permitir/denegar acceso
   - Registro básico del evento

4. **Registro de Eventos Básico**
   - Almacenar eventos de acceso (permitido/denegado)
   - Información básica: persona, fecha/hora, resultado
   - Consulta simple de eventos recientes

#### 2.2.2. Objetivos Técnicos del MVP

1. **Arquitectura Simple**
   - Aplicación monolítica o de 2 capas (backend + frontend)
   - API REST básica
   - Base de datos simple (SQLite o PostgreSQL básico)
   - Sin requerimientos de alta disponibilidad

2. **Seguridad Básica**
   - Autenticación simple (usuario/contraseña o JWT básico)
   - Sin encriptación avanzada (para MVP)
   - Logging básico

3. **Rendimiento Aceptable**
   - Funcional para demostración
   - Sin optimizaciones avanzadas
   - Soporte para 10-20 personas registradas

4. **Tecnologías Simplificadas**
   - Python (FastAPI o Flask) para backend
   - React o HTML simple para frontend
   - SQLite o PostgreSQL básico
   - Librería de reconocimiento facial pre-entrenada (face_recognition, DeepFace, etc.)

### 2.3. Alcance del MVP

#### 2.3.1. Alcance Funcional Incluido en MVP

✅ **Registro Básico de Personas**
- Formulario web simple para registrar personas
- Campos: nombre, documento de identidad, tipo (empleado/visitante)
- Captura de foto facial (webcam o archivo)
- Generación y almacenamiento de embedding facial
- Estado activo/inactivo

✅ **Reconocimiento Facial Básico**
- Detección de rostros en imágenes
- Generación de embeddings faciales
- Comparación de embeddings para identificación
- Tolerancia configurable de similitud

✅ **Validación de Acceso Básica**
- Endpoint API: POST /api/validate-access
- Recibe imagen facial
- Compara con embeddings almacenados
- Retorna: permitido/denegado + información de persona identificada

✅ **Registro de Eventos Básico**
- Almacenar cada intento de acceso
- Información: persona identificada (o "desconocido"), fecha/hora, resultado
- Lista simple de eventos recientes en interfaz web

✅ **Interfaz Web Mínima**
- Página para registrar personas
- Página para probar reconocimiento facial (subir foto)
- Lista de eventos recientes
- Autenticación básica (usuario/contraseña)

#### 2.3.2. Alcance Funcional Excluido del MVP

❌ **Sistema de Autorizaciones Complejo**
- No se implementará gestión de autorizaciones con fechas
- En MVP, todas las personas activas tienen acceso

❌ **Método Alternativo de Identificación**
- Solo reconocimiento facial en MVP
- No se implementa identificación por documento

❌ **Integración con Dispositivos Físicos**
- No se integra con torniquetes o puertas automáticas
- Solo API para pruebas manuales

❌ **Reportes Avanzados**
- Solo lista básica de eventos
- No hay reportes, gráficos o análisis

❌ **Gestión de Usuarios del Sistema**
- Un solo usuario administrador
- Sin roles ni permisos

❌ **Optimizaciones de Rendimiento**
- Sin caché, sin optimizaciones avanzadas
- Funcional para demostración con pocos usuarios

#### 2.3.3. Alcance Técnico del MVP

**Tecnologías Simplificadas:**
- **Backend**: Python (FastAPI o Flask)
- **IA/ML**: Librería pre-entrenada (face_recognition, DeepFace, o MediaPipe)
- **Base de Datos**: SQLite (desarrollo) o PostgreSQL (producción simple)
- **Frontend**: React simple o HTML/CSS/JavaScript básico
- **Autenticación**: JWT básico o sesiones simples
- **Infraestructura**: Servidor único, sin Docker/Kubernetes (opcional)

**Entregables del MVP:**
- Código fuente funcional
- Base de datos con esquema mínimo
- Documentación básica de instalación
- Instrucciones de uso
- Demo funcional

---

## 3. Cronograma y Tareas - MVP (3 Semanas)

### 3.1. Metodología de Desarrollo

El MVP se desarrollará utilizando un enfoque **ágil y pragmático**, con desarrollo rápido y funcionalidades mínimas viables. Se prioriza la funcionalidad sobre la perfección.

### 3.2. Fases del MVP

El proyecto se divide en **3 fases principales** con una duración total de **3 semanas**:

1. **Semana 1: Configuración y Módulo de Reconocimiento Facial** (5 días)
2. **Semana 2: Backend y Base de Datos** (5 días)
3. **Semana 3: Frontend, Integración y Pruebas** (5 días)

### 3.3. Desglose de Tareas del MVP

#### SEMANA 1: CONFIGURACIÓN Y MÓDULO DE RECONOCIMIENTO FACIAL

**Día 1: Configuración Inicial**
- **Tarea 1.1**: Configuración del entorno de desarrollo
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: Entorno Python configurado, dependencias instaladas

- **Tarea 1.2**: Investigación y selección de librería de reconocimiento facial
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: Librería seleccionada (face_recognition, DeepFace, o MediaPipe)

**Día 2-3: Desarrollo del Módulo de Reconocimiento Facial**
- **Tarea 1.3**: Integración de librería de reconocimiento facial
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: Script funcional que detecta rostros y genera embeddings

- **Tarea 1.4**: Desarrollo de función de comparación de embeddings
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: Función que compara embeddings y retorna similitud

**Día 4-5: Pruebas y Refinamiento del Módulo de IA**
- **Tarea 1.5**: Pruebas del módulo de reconocimiento facial
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: Módulo probado con diferentes imágenes

- **Tarea 1.6**: Ajuste de tolerancia y parámetros
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: Parámetros optimizados para mejor precisión

- **Tarea 1.7**: Documentación básica del módulo
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: README con instrucciones de uso

#### SEMANA 2: BACKEND Y BASE DE DATOS

**Día 1: Diseño e Implementación de Base de Datos**
- **Tarea 2.1**: Diseño del esquema de base de datos mínimo
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: Esquema SQL (3 tablas: persona, reconocimiento_facial, registro_acceso)

- **Tarea 2.2**: Creación de base de datos y tablas
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: Base de datos SQLite/PostgreSQL creada

**Día 2-3: Desarrollo de API REST Básica**
- **Tarea 2.3**: Configuración de FastAPI/Flask
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: Servidor API básico funcionando

- **Tarea 2.4**: Endpoint de registro de personas (POST /api/personas)
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: Endpoint que recibe datos y foto, genera embedding, almacena en BD

- **Tarea 2.5**: Endpoint de validación de acceso (POST /api/validate-access)
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: Endpoint que recibe foto, identifica persona, registra evento

- **Tarea 2.6**: Endpoint de consulta de eventos (GET /api/eventos)
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: Endpoint que retorna lista de eventos recientes

**Día 4-5: Integración y Pruebas del Backend**
- **Tarea 2.7**: Integración del módulo de IA con la API
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: API completamente funcional con reconocimiento facial

- **Tarea 2.8**: Pruebas de los endpoints
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Backend
  - **Entregables**: Endpoints probados y funcionando correctamente

#### SEMANA 3: FRONTEND, INTEGRACIÓN Y PRUEBAS

**Día 1-2: Desarrollo del Frontend Básico**
- **Tarea 3.1**: Configuración de frontend (React simple o HTML/CSS/JS)
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Frontend
  - **Entregables**: Estructura básica de frontend

- **Tarea 3.2**: Página de registro de personas
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Frontend
  - **Entregables**: Formulario con captura de foto (webcam o archivo)

- **Tarea 3.3**: Página de prueba de reconocimiento facial
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Frontend
  - **Entregables**: Página para subir foto y probar reconocimiento

**Día 3: Integración Frontend-Backend**
- **Tarea 3.4**: Integración de frontend con API
  - **Duración**: 1 día
  - **Responsable**: Desarrollador Full-Stack
  - **Entregables**: Frontend conectado con backend, flujo completo funcional

**Día 4: Página de Eventos y Ajustes**
- **Tarea 3.5**: Página de lista de eventos
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Frontend
  - **Entregables**: Página que muestra eventos recientes

- **Tarea 3.6**: Ajustes de UI/UX básicos
  - **Duración**: 0.5 día
  - **Responsable**: Desarrollador Frontend
  - **Entregables**: Interfaz mejorada y funcional

**Día 5: Pruebas Finales y Documentación**
- **Tarea 3.7**: Pruebas end-to-end del sistema completo
  - **Duración**: 1 día
  - **Responsable**: Todo el equipo
  - **Entregables**: Sistema probado, bugs corregidos

- **Tarea 3.8**: Documentación básica de instalación y uso
  - **Duración**: 0.5 día (paralelo)
  - **Responsable**: Desarrollador
  - **Entregables**: README con instrucciones

- **Tarea 3.9**: Preparación de demo
  - **Duración**: 0.5 día
  - **Responsable**: Todo el equipo
  - **Entregables**: Demo funcional lista para presentación

### 3.4. Diagrama de Gantt - MVP (3 Semanas)

```
SEMANA 1: CONFIGURACIÓN Y MÓDULO DE RECONOCIMIENTO FACIAL
═══════════════════════════════════════════════════════════════════════════════
Día 1:  Configuración inicial                    ██░░░░░░░░░░░░░░░░░░░░░░░░░░░░
         Investigación librería IA                ░░██░░░░░░░░░░░░░░░░░░░░░░░░░░
Día 2:  Integración librería reconocimiento      ░░░░████░░░░░░░░░░░░░░░░░░░░░░
Día 3:  Función comparación embeddings            ░░░░░░░░████░░░░░░░░░░░░░░░░░░
Día 4:  Pruebas módulo IA                         ░░░░░░░░░░░░████░░░░░░░░░░░░░░
Día 5:  Ajuste parámetros + documentación          ░░░░░░░░░░░░░░░░████░░░░░░░░░░

SEMANA 2: BACKEND Y BASE DE DATOS
═══════════════════════════════════════════════════════════════════════════════
Día 6:  Diseño BD + Creación tablas               ░░░░░░░░░░░░░░░░░░░░████░░░░░░
Día 7:  Configuración FastAPI/Flask               ░░░░░░░░░░░░░░░░░░░░░░░░██░░░░
         Endpoint registro personas                ░░░░░░░░░░░░░░░░░░░░░░░░██░░░░
Día 8:  Endpoint validación acceso                ░░░░░░░░░░░░░░░░░░░░░░░░░░████
Día 9:  Endpoint consulta eventos                 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
         Integración módulo IA con API            ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
Día 10: Pruebas endpoints                         ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██

SEMANA 3: FRONTEND, INTEGRACIÓN Y PRUEBAS
═══════════════════════════════════════════════════════════════════════════════
Día 11: Configuración frontend                    ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
         Página registro personas                 ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
Día 12: Página prueba reconocimiento              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
         Integración frontend-backend              ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
Día 13: Página lista eventos                      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
         Ajustes UI/UX                            ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
Día 14: Pruebas end-to-end                        ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██
Día 15: Documentación + Demo                      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██

Leyenda: █ = Tarea activa, ░ = Tiempo no asignado

Semanas: 1 (Días 1-5)    2 (Días 6-10)    3 (Días 11-15)
```

### 3.5. Hitos del MVP

| Hito | Descripción | Semana | Entregable |
|------|-------------|--------|------------|
| **H1** | Módulo de Reconocimiento Facial Funcional | 1 | Script de reconocimiento facial operativo |
| **H2** | Backend y API REST Completos | 2 | API REST funcional con todos los endpoints |
| **H3** | MVP Completo y Funcional | 3 | Sistema completo listo para demo |

### 3.6. Recursos Necesarios para MVP

#### Equipo de Trabajo - Grupo 1

**Participantes del Proyecto:**

| Participante | Rol |
|--------------|-----|
| **Edgar Mauricio Cifuentes** | Líder Técnico |
| **Elkyn Fabián Enríquez** | Líder Infraestructura / DevOps |
| **Hugo Hernán Rodríguez Holguín** | Líder Arquitecto |
| **Juan Sebastián Bohórquez** | Líder Testing / Calidad |

#### Roles y Responsabilidades

##### Líder Técnico
- **Responsable:** Edgar Mauricio Cifuentes
- **Responsabilidad:** Asegurar calidad del desarrollo y prácticas de código.
- **Tareas:**
  - Code reviews
  - Definir linters/formatters
  - Resolver blockers técnicos
- **Entregable:** Guidelines de desarrollo y checklist de revisión.
- **KPI:** Tiempo medio de review (<48h).

##### Líder Arquitecto
- **Responsable:** Hugo Hernán Rodríguez Holguín
- **Responsabilidad:** Decisiones arquitectónicas y coherencia técnica.
- **Tareas:**
  - Definir diagramas
  - Aprobar ADRs (Architecture Decision Records)
  - Validar dependencias críticas
- **Entregable:** Diagrama arquitectónico y ADRs aprobadas.
- **KPI:** Número de ADRs implementadas.

##### Líder Infraestructura / DevOps
- **Responsable:** Elkyn Fabián Enríquez
- **Responsabilidad:** CI/CD, despliegues y disponibilidad.
- **Tareas:**
  - Pipelines reproducibles
  - Infrastructure as Code (IaC)
  - Monitorización y runbooks
- **Entregable:** Workflows CI/CD y runbooks de despliegue.
- **KPI:** % despliegues sin rollback.

##### Líder Testing / Calidad
- **Responsable:** Juan Sebastián Bohórquez
- **Responsabilidad:** Estrategia y automatización de pruebas.
- **Tareas:**
  - Crear suites de tests
  - Integrar en CI
  - Reportes de cobertura
- **Entregable:** Pipelines de test y reportes de QA.
- **KPI:** Cobertura mínima y regresiones en producción.

**Nota:** Para un MVP de 3 semanas, este equipo de 4 líderes especializados trabajará de forma colaborativa, con cada líder enfocándose en su área de expertise mientras contribuyen al desarrollo del MVP.

#### Infraestructura y Herramientas Mínimas

- **Servidor de Desarrollo**: 1 computadora personal o servidor básico
- **Base de Datos**: SQLite (desarrollo) o PostgreSQL (producción simple)
- **Herramientas de Desarrollo**: 
  - Python 3.8+
  - FastAPI o Flask
  - React o HTML/CSS/JavaScript básico
  - Git para control de versiones
- **Librerías de IA**: 
  - face_recognition (recomendado para MVP) o
  - DeepFace o
  - MediaPipe
- **Sin requerimientos especiales**: No se requiere GPU para MVP (modelos pre-entrenados)

### 3.7. Riesgos y Mitigaciones del MVP

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|---------------|---------|------------|
| **Rendimiento del modelo de IA insuficiente** | Media | Medio | Usar librerías pre-entrenadas probadas (face_recognition), ajustar tolerancia |
| **Retrasos en desarrollo** | Alta | Alto | Priorizar funcionalidades mínimas, simplificar al máximo |
| **Problemas de precisión en reconocimiento** | Media | Medio | Ajustar parámetros de tolerancia, usar múltiples fotos de referencia |
| **Falta de tiempo para completar MVP** | Alta | Alto | Enfoque en funcionalidad básica, dejar mejoras para iteraciones futuras |
| **Problemas técnicos con librerías** | Baja | Medio | Tener librería alternativa identificada (DeepFace como backup) |

---

## 4. Conclusiones

Este MVP representa una oportunidad para validar rápidamente la viabilidad técnica del reconocimiento facial para control de acceso en STI S.A.S.

El MVP, con una duración de **3 semanas**, permitirá:

- **Validar el concepto**: Demostrar que el reconocimiento facial funciona para el caso de uso
- **Obtener retroalimentación temprana**: Probar con usuarios reales y ajustar según feedback
- **Establecer base técnica**: Crear la base para futuras iteraciones y mejoras
- **Demostrar valor**: Mostrar a stakeholders el potencial de la solución

**Próximos Pasos después del MVP:**
- Iteración 2: Mejoras de precisión y rendimiento
- Iteración 3: Sistema de autorizaciones completo
- Iteración 4: Integración con dispositivos físicos
- Iteración 5: Reportes avanzados y optimizaciones

La metodología de MVP permite validar rápidamente la idea, obtener retroalimentación y decidir si vale la pena invertir en el desarrollo completo del sistema.

---

**Documento elaborado por:** Equipo de Desarrollo STI S.A.S.  
**Fecha:** 2026  
**Versión:** MVP 1.0
