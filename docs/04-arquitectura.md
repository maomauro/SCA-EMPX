# 🏗️ Arquitectura del Sistema

## 1. Introducción

Este documento describe la arquitectura del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)**. La arquitectura está diseñada para ser escalable, segura y mantenible, cumpliendo con los requerimientos funcionales y no funcionales definidos.

**Característica principal**: El sistema utiliza **reconocimiento facial** como método principal de identificación y validación de acceso. **Para el MVP** se usan **librerías pre-entrenadas** (face_recognition, DeepFace o MediaPipe); en iteraciones futuras podrían incorporarse YOLOv8 (detección) y ArcFace (embeddings). Todas las personas deben tener su embedding facial registrado para poder ingresar. El alcance del MVP (sin servicio de autorizaciones ni integración con dispositivos físicos) está definido en [08-definicion-proyecto.md](./08-definicion-proyecto.md).

---

## 2. Principios Arquitectónicos

### 2.1. Principios de Diseño

- **Separación de responsabilidades**: Cada componente tiene una responsabilidad clara y bien definida
- **Modularidad**: Sistema compuesto por módulos independientes y reutilizables
- **Escalabilidad**: Arquitectura que permite crecer horizontal y verticalmente
- **Seguridad por diseño**: Seguridad integrada en todos los niveles
- **Trazabilidad**: Todos los eventos críticos son registrados
- **Rendimiento**: Optimización para respuestas en tiempo real

### 2.2. Patrones Arquitectónicos

- **Arquitectura en capas**: Separación clara entre presentación, lógica de negocio y datos
- **API REST**: Comunicación estándar entre componentes
- **Microservicios** (opcional): Para componentes que requieren escalabilidad independiente
- **Repository Pattern**: Abstracción de acceso a datos

---

## 3. Arquitectura Lógica

### 3.1. Vista General

La arquitectura del sistema se organiza en las siguientes capas:

```
┌───────────────────────────────────────────────────────────┐
│           CAPA DE PRESENTACIÓN                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ Portal Web   │  │ Panel        │  │ App Móvil    │     │
│  │ Admin        │  │ Monitoreo    │  │ (Opcional)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│        CAPA DE INTEGRACIÓN CON DISPOSITIVOS               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │ API REST     │  │ WebSocket    │  │ Integración  │     │
│  │ Dispositivos │  │ Tiempo Real  │  │ Legacy       │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────────────────────────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────────────────┐
│        CAPA DE SERVICIOS DE NEGOCIO                       │
│  ┌──────────────┐  ┌────────────────┐  ┌──────────────┐   │
│  │ Gestión      │  │ Autorizaciones*│  │ Control      │   │  *Fuera del MVP
│  │ Personas     │  │                │  │ Acceso       │   │
│  └──────────────┘  └────────────────┘  └──────────────┘   │
│  ┌──────────────┐  ┌────────────────┐                     │
│  │ Auditoría    │  │ Notificaciones │                     │
│  │ Reportes     │  │                │                     │
│  └──────────────┘  └────────────────┘                     │
└───────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│        CAPA DE SEGURIDAD                                │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │ Autenticación│  │ Autorización  │  │ Cifrado      │  │
│  │              │  │ (RBAC)        │  │              │  │
│  └──────────────┘  └───────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│        CAPA DE DATOS                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │
│  │ BD           │  │ Cache        │  │ Logs         │   │
│  │ Transaccional│  │ (Redis)      │  │ Auditoría    │   │
│  └──────────────┘  └──────────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 4. Descripción de Capas

### 4.1. Capa de Presentación

#### 4.1.1. Portal Web de Administración

**Descripción**:  
Interfaz web para usuarios administrativos (RRHH, Seguridad, Recepción).

**Tecnologías sugeridas**:
- Framework frontend: React, Vue.js o Angular
- Estilos: CSS/SCSS, framework UI (Material-UI, Bootstrap)
- Estado: Redux, Vuex o Context API

**Funcionalidades**:
- Gestión de empleados y visitantes
- Configuración de autorizaciones
- Consulta de historial y reportes
- Administración de usuarios del sistema

**Características**:
- Responsive design (móvil y escritorio)
- Autenticación mediante tokens (JWT)
- Navegación intuitiva por roles

#### 4.1.2. Panel de Monitoreo

**Descripción**:  
Dashboard en tiempo real para monitoreo de accesos y eventos.

**Funcionalidades**:
- Visualización de accesos en tiempo real
- Métricas y estadísticas
- Alertas de eventos críticos
- Mapa de puntos de acceso

**Características**:
- Actualización en tiempo real (WebSocket)
- Gráficos y visualizaciones interactivas

#### 4.1.3. Aplicación Móvil (Opcional)

**Descripción**:  
Aplicación móvil para recepcionistas y administradores.

**Funcionalidades**:
- Registro rápido de visitantes
- Consulta de información básica
- Notificaciones push

---

### 4.2. Capa de Integración con Dispositivos

#### 4.2.1. API REST para Dispositivos

**Descripción**:  
API REST para validación de acceso. En MVP se usa para pruebas (sin integración con torniquetes/lectores); en iteraciones futuras permitirá a dispositivos físicos comunicarse con el sistema.

**Endpoints principales**:
```
POST /api/v1/access/validate-face
  - Validar acceso por reconocimiento facial (MÉTODO PRINCIPAL)
  - Body: { "image": "base64_encoded_image", "timestamp": "..." }
  - Respuesta: { "allowed": true/false, "reason": "...", "person_id": 123, "similarity": 0.85 }

POST /api/v1/access/validate-document
  - Validar acceso por documento (MÉTODO ALTERNATIVO)
  - Body: { "document": "12345678", "timestamp": "..." }
  - Respuesta: { "allowed": true/false, "reason": "...", "person_id": 123 }

POST /api/v1/access/register
  - Registrar evento de acceso (entrada/salida)
  - Body: { "person_id", "tipo_movimiento", "metodo_identificacion", "result", "similarity_score", "timestamp" }
```

**Características**:
- Autenticación mediante API keys o tokens
- Respuesta rápida: < 4 segundos (reconocimiento facial), < 2 segundos (documento)
- Formato JSON estándar
- Versionado de API (v1, v2, ...)

#### 4.2.2. WebSocket para Tiempo Real (Opcional)

**Descripción**:  
Conexión WebSocket para comunicación bidireccional en tiempo real.

**Uso**:
- Notificaciones push a dispositivos
- Actualización de configuración en tiempo real
- Monitoreo de estado de dispositivos

#### 4.2.3. Integración Legacy (Opcional)

**Descripción**:  
Adaptadores para sistemas legacy que no soportan REST.

**Ejemplos**:
- Integración con sistemas de control de acceso existentes
- Protocolos propietarios de fabricantes

---

### 4.3. Capa de Servicios de Negocio

#### 4.3.1. Servicio de Gestión de Personas

**Responsabilidades**:
- CRUD de empleados y visitantes
- Validación de datos
- Gestión de credenciales
- Sincronización con sistemas externos (RRHH, opcional)

**Operaciones principales**:
- `createEmployee(employeeData)`
- `updateEmployee(id, employeeData)`
- `deactivateEmployee(id)`
- `createVisitor(visitorData)`
- `getPersonById(id)`
- `getPersonByCredential(credential)`

#### 4.3.2. Servicio de Autorizaciones *(fuera del MVP)*

**Responsabilidades** (iteraciones futuras):
- Gestión de autorizaciones de acceso
- Validación de vigencias (fecha, hora)
- Gestión de permisos de acceso
- Revocación de autorizaciones

**Operaciones principales**:
- `createAuthorization(authorizationData)`
- `validateAuthorization(personId, zoneId, timestamp)`
- `revokeAuthorization(authorizationId)`
- `getActiveAuthorizations(personId)`

#### 4.3.3. Servicio de Reconocimiento Facial

**Responsabilidades**:
- Generación de embeddings faciales (MVP: librería pre-entrenada como face_recognition, DeepFace o MediaPipe; futuras iteraciones: ArcFace)
- Detección de rostros (MVP: misma librería pre-entrenada; futuras iteraciones: YOLOv8)
- Comparación de embeddings (similaridad coseno)
- Gestión de embeddings almacenados

**Operaciones principales**:
- `generateEmbedding(image)`: Genera embedding facial de una imagen
  - Retorna: `{ embedding: float[], quality: float, face_detected: boolean }`
- `registerFacialEmbedding(personId, image)`: Registra embedding para una persona
  - Retorna: `{ success: boolean, embedding_id: number }`
- `identifyPerson(image)`: Identifica persona por reconocimiento facial
  - Retorna: `{ person_id: number, similarity: float, confidence: float }` o `null`
- `compareEmbeddings(embedding1, embedding2)`: Compara dos embeddings
  - Retorna: `similarity_score` (0-1)

**Tecnologías**: MVP: face_recognition, DeepFace o MediaPipe (pre-entrenadas). Futuras iteraciones: YOLOv8 (detección), ArcFace (embeddings).
- **Similaridad coseno** (o distancia euclidiana): Para comparar embeddings

**Flujo de reconocimiento**:
1. Captura de imagen en tiempo real
2. Detección de rostro (modelo pre-entrenado en MVP)
3. Extracción de características (embedding)
4. Comparación con embeddings almacenados
5. Retornar persona identificada si similarity > umbral

#### 4.3.4. Servicio de Control de Acceso

**Responsabilidades**:
- Validación en tiempo real de acceso
- Verificación por documento o reconocimiento facial
- Verificación de estado de persona
- Verificación de autorizaciones vigentes

**Operaciones principales**:
- `validateAccessByDocument(document)`: Validación por documento
  - Retorna: `{ allowed: boolean, reason: string, personId: number }`
- `validateAccessByFace(image)`: Validación por reconocimiento facial
  - Retorna: `{ allowed: boolean, reason: string, personId: number, similarity: float }`

**Flujo de validación (por documento)**:
1. Buscar persona por documento
2. Verificar que persona existe y está activa
3. Verificar autorización vigente (fecha de inicio y fin)
4. Retornar resultado

**Flujo de validación (por reconocimiento facial)**:
1. Identificar persona usando Servicio de Reconocimiento Facial
2. Verificar que persona existe y está activa
3. Verificar autorización vigente (fecha de inicio y fin)
4. Retornar resultado

#### 4.3.5. Servicio de Auditoría y Reportes

**Responsabilidades**:
- Registro de eventos de acceso
- Consultas de historial
- Generación de reportes
- Exportación de datos

**Operaciones principales**:
- `registerAccessEvent(eventData)`
- `getAccessHistory(filters)`
- `generateReport(reportType, parameters)`
- `exportData(format, filters)`

#### 4.3.6. Servicio de Notificaciones (Opcional)

**Responsabilidades**:
- Envío de notificaciones (email, SMS, push)
- Alertas de eventos críticos
- Notificaciones a administradores

---

### 4.4. Capa de Seguridad

#### 4.4.1. Autenticación

**Mecanismos**:
- Autenticación basada en tokens (JWT)
- Integración opcional con LDAP/Active Directory
- Autenticación de dos factores (2FA) para administradores

**Flujo**:
1. Usuario envía credenciales (usuario/contraseña)
2. Sistema valida credenciales
3. Sistema genera token JWT
4. Cliente usa token en requests posteriores

#### 4.4.2. Autorización (RBAC)

**Roles definidos**:
- **Administrador del Sistema**: Acceso completo
- **Administrador de Seguridad**: Gestión de seguridad, auditoría
- **RRHH**: Gestión de empleados
- **Recepcionista**: Gestión de visitantes
- **Empleado**: Solo consulta propia
- **Visitante**: Sin acceso al sistema

**Permisos**:
- Permisos granulares por recurso y acción
- Ejemplo: `employees:create`, `visitors:read`, `reports:export`

#### 4.4.3. Cifrado

**Datos en tránsito**:
- HTTPS/TLS 1.2+ para todas las comunicaciones
- Certificados SSL válidos

**Datos en reposo**:
- Cifrado de campos sensibles (contraseñas, datos biométricos)
- Hash seguro para contraseñas (bcrypt, Argon2)
- Cifrado de base de datos (opcional, según requerimientos)

---

### 4.5. Capa de Datos

#### 4.5.1. Base de Datos Transaccional

**Tecnología sugerida**: PostgreSQL, MySQL o SQL Server

**Características**:
- ACID compliance
- Transacciones para operaciones críticas
- Índices para optimización de consultas
- Backups regulares

**Estructura**:
- Ver documento de Modelo de Datos para esquema completo

#### 4.5.2. Cache (Redis)

**Uso**:
- Cache de validaciones de acceso frecuentes
- Cache de autorizaciones activas
- Sesiones de usuario
- Rate limiting

**Estrategia**:
- TTL corto para datos dinámicos (autorizaciones: 5 minutos)
- Invalidación cuando se actualizan datos

#### 4.5.3. Almacén de Logs y Auditoría

**Características**:
- Logs inmutables
- Almacenamiento separado para auditoría
- Retención configurable (mínimo 5 años)
- Integridad verificable (hashes)

**Tecnologías**:
- Base de datos separada para logs
- O sistema de logging centralizado (ELK Stack, opcional)

---

## 5. Flujo de Datos Típico

### 5.1. Flujo de Validación de Acceso por Documento

```
1. Persona presenta documento en punto de acceso
   ↓
2. Dispositivo/envía POST /api/v1/access/validate
   { "document": "12345678", "timestamp": "..." }
   ↓
3. API REST recibe solicitud
   ↓
4. Servicio de Control de Acceso:
   a. Busca persona por documento (cache o BD)
   b. Verifica estado activo
   c. Verifica autorización vigente
   d. Retorna resultado
   ↓
5. API REST retorna respuesta:
   { "allowed": true/false, "reason": "...", "person_id": 123 }
   ↓
6. Dispositivo (fuera del MVP; en MVP solo API): Si allowed=true en futuro desbloquea torniquete; si false, mensaje de denegación.
   ↓
7. Servicio de Auditoría registra evento en BD
```

### 5.1A. Flujo de Validación de Acceso por Reconocimiento Facial

```
1. Cámara captura imagen de la persona
   ↓
2. Dispositivo/envía POST /api/v1/access/validate-face
   { "image": "base64_encoded_image", "timestamp": "..." }
   ↓
3. API REST recibe solicitud
   ↓
4. Servicio de Reconocimiento Facial:
   a. Detecta rostro (modelo pre-entrenado: face_recognition/DeepFace/MediaPipe en MVP)
   b. Genera embedding
   c. Compara con embeddings almacenados (similaridad coseno)
   d. Identifica persona si similarity > umbral (ej. 0.7)
   ↓
5. Servicio de Control de Acceso:
   a. Verifica que persona existe y está activa
   b. (MVP: no verifica autorización; en iteraciones futuras: autorización vigente)
   c. Retorna resultado
   ↓
6. API REST retorna respuesta:
   { "allowed": true/false, "reason": "...", "person_id": 123, "similarity": 0.85 }
   ↓
7. Cliente/Dispositivo (MVP: pruebas vía API; futuras iteraciones: desbloqueo de torniquete):
   - Si allowed=true: Acceso permitido (en futuro: desbloquea torniquete)
   - Si allowed=false: Muestra mensaje de denegación
   ↓
8. Servicio de Auditoría registra evento en BD (con similarity score)
```

### 5.2. Flujo de Registro de Visitante

```
1. Recepcionista accede al portal web
   ↓
2. Autenticación (JWT token)
   ↓
3. Recepcionista completa formulario de visitante
   ↓
4. Frontend envía POST /api/v1/visitors
   ↓
5. Servicio de Gestión de Personas:
   a. Valida datos
   b. Crea registro de visitante
   ↓
6. Si se proporciona foto facial:
   a. Servicio de Reconocimiento Facial genera embedding
   b. Almacena embedding en BD
   ↓
7. (Fuera del MVP) Servicio de Autorizaciones: crea autorización con vigencia limitada. En MVP no se implementa.
   ↓
8. Respuesta al frontend con datos del visitante
   ↓
9. Frontend muestra confirmación de registro
```

---

## 6. Consideraciones de Despliegue

### 6.1. Arquitectura de Despliegue

**Opciones**:
- **Monolito modular**: Aplicación única con módulos separados (recomendado para inicio)
- **Microservicios**: Servicios independientes (para escalabilidad futura)

### 6.2. Infraestructura

**Componentes**:
- Servidor de aplicación (backend)
- Servidor de base de datos
- Servidor web (Nginx, Apache) para frontend
- Redis para cache
- Load balancer (si hay múltiples instancias)

### 6.3. Escalabilidad

**Horizontal**:
- Múltiples instancias del backend detrás de load balancer
- Base de datos con réplicas de lectura

**Vertical**:
- Aumento de recursos (CPU, RAM) según necesidad

### 6.4. Alta Disponibilidad

**Estrategias**:
- Redundancia de servidores
- Base de datos con réplicas
- Failover automático
- Backups regulares y probados

---

## 7. Tecnologías Sugeridas

### 7.1. Backend

- **Lenguaje**: Python (Django/FastAPI), Node.js (Express/NestJS), Java (Spring Boot), o .NET
- **Framework**: Según lenguaje elegido
- **ORM**: Django ORM, Sequelize, Hibernate, Entity Framework

### 7.1.1. Servicio de Reconocimiento Facial (IA)

- **Lenguaje**: Python (recomendado para IA)
- **Framework**: FastAPI o Flask (microservicio o monolito)
- **MVP – Modelos/Librerías pre-entrenadas** (definido en 08-definicion-proyecto.md):
  - **face_recognition**, **DeepFace** o **MediaPipe**: Detección de rostros y generación de embeddings en un solo paquete
  - `opencv-python`, `numpy`; opcionalmente `scikit-learn` para similaridad coseno
- **Iteraciones futuras** (opcional):
  - **YOLOv8**: Detección de rostros (`ultralytics`)
  - **ArcFace**: Embeddings (`insightface` o `arcface-pytorch`)
- **GPU**: Opcional; para MVP no requerido

### 7.2. Frontend

- **Framework**: React, Vue.js o Angular
- **Estado**: Redux, Vuex, NgRx
- **HTTP Client**: Axios, Fetch API

### 7.3. Base de Datos

- **Principal**: PostgreSQL (recomendado), MySQL, SQL Server
- **Cache**: Redis
- **Logs**: PostgreSQL o sistema de logging (ELK Stack)

### 7.4. Infraestructura

- **Contenedores**: Docker (opcional)
- **Orquestación**: Docker Compose, Kubernetes (opcional)
- **Servidor Web**: Nginx, Apache
- **CI/CD**: GitHub Actions, GitLab CI, Jenkins

---

## 8. Seguridad

### 8.1. Medidas de Seguridad

- Autenticación y autorización en todos los endpoints
- Validación de entrada (sanitización, validación de tipos)
- Protección contra SQL injection (ORM parametrizado)
- Protección contra XSS (escapado de salida)
- Protección contra CSRF (tokens)
- Rate limiting en APIs públicas
- Logs de seguridad para auditoría

### 8.2. Cumplimiento

- Políticas de seguridad de STI S.A.S.
- Protección de datos personales
- Retención de logs según políticas

---

**Documento**: Arquitectura del Sistema  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
