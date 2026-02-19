# 📋 Especificación de Requerimientos (SRS)

## 1. Introducción

### 1.1. Propósito del Documento

Este documento especifica los requerimientos funcionales y no funcionales del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** para Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.).

### 1.2. Alcance del Sistema

**Nombre del sistema:**  
Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)

**Propósito:**  
Gestionar el acceso físico a las instalaciones de STI S.A.S., permitiendo el ingreso solo a personas registradas, autorizadas y en estado activo, registrando además sus entradas y salidas con trazabilidad completa.

**Alcance funcional (visión completa):**
- Registro y gestión de empleados y visitantes
- Gestión de autorizaciones de acceso (fuera del MVP; ver 08-definicion-proyecto.md)
- Control de acceso en torniquetes/puertas automáticas (fuera del MVP)
- Registro de eventos de entrada y salida
- Consultas y reportes de auditoría (MVP: solo lista básica de eventos)
- Gestión de usuarios del sistema (fuera del MVP; MVP: un solo usuario administrador)

> **Alcance del MVP (3 semanas):** Registro básico de personas, reconocimiento facial con librerías pre-entrenadas (face_recognition, DeepFace, MediaPipe), validación básica de acceso (API) y registro de eventos. Excluido en MVP: autorizaciones complejas, identificación por documento, integración con dispositivos físicos. Referencia: [08-definicion-proyecto.md](./08-definicion-proyecto.md).

**Alcance técnico:**
- Portal web de administración
- API REST para integración con dispositivos físicos
- Base de datos transaccional
- Sistema de autenticación y autorización
- Módulo de auditoría y reportes

### 1.3. Definiciones, Acrónimos y Abreviaciones

- **SCA-EMPX**: Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas
- **STI S.A.S.**: Soluciones Tecnológicas Integrales S.A.S.
- **RF**: Requerimiento Funcional
- **RNF**: Requerimiento No Funcional
- **API**: Application Programming Interface
- **RRHH**: Recursos Humanos
- **BPMN**: Business Process Model and Notation

### 1.4. Referencias

- Documento de Contexto Empresarial
- Caso de Negocio
- Políticas de Seguridad de STI S.A.S.

---

## 2. Descripción General

### 2.1. Perspectiva del Producto

El sistema SCA-EMPX es un sistema independiente que se integra con:
- Dispositivos físicos de control de acceso (torniquetes, lectores de tarjetas, sistemas biométricos)
- Sistemas de RRHH (para sincronización de empleados, opcional)
- Sistemas de seguridad (para reportes y alertas, opcional)

### 2.2. Funciones del Producto

El sistema proporciona las siguientes funciones principales:

1. **Gestión de Personas**: Registro y administración de empleados y visitantes
2. **Gestión de Autorizaciones**: Configuración de permisos de acceso por persona
3. **Control de Acceso**: Validación en tiempo real de credenciales y autorizaciones
4. **Registro de Eventos**: Captura automática de entradas y salidas
5. **Auditoría y Reportes**: Consultas y reportes de accesos históricos
6. **Administración**: Gestión de usuarios, roles y configuración del sistema

### 2.3. Características de los Usuarios

El sistema está dirigido a los siguientes tipos de usuarios:

- **Empleados**: Usuarios finales que utilizan el sistema para ingresar/salir
- **Visitantes**: Personas externas que requieren acceso temporal
- **Recepcionistas**: Personal que registra visitantes y gestiona autorizaciones
- **Administradores de Seguridad**: Personal que configura reglas y consulta auditoría
- **RRHH**: Personal que gestiona altas/bajas de empleados
- **Administradores del Sistema**: Personal técnico que administra el sistema

---

## 3. Actores del Sistema

### 3.1. Empleado
**Descripción**: Persona de planta permanente o contratista con acceso recurrente a las instalaciones.

**Responsabilidades**:
- Presentar credencial para ingresar/salir
- Mantener credencial en buen estado

**Características**:
- Acceso recurrente y permanente (mientras esté activo)

### 3.2. Visitante
**Descripción**: Persona externa que ingresa a las instalaciones por una visita específica.

**Responsabilidades**:
- Proporcionar información de identificación
- Respetar fechas de autorización

**Características**:
- Acceso temporal y limitado
- Requiere autorización previa o en el momento

### 3.3. Recepcionista
**Descripción**: Personal de recepción que registra visitantes y gestiona autorizaciones puntuales.

**Responsabilidades**:
- Registrar datos de visitantes
- Generar autorizaciones de acceso
- Validar identidad de visitantes

**Permisos**:
- Crear y editar registros de visitantes
- Generar autorizaciones temporales
- Consultar historial de visitantes

### 3.4. Administrador de Seguridad
**Descripción**: Personal responsable de la seguridad que configura reglas, consulta auditoría y gestiona accesos.

**Responsabilidades**:
- Configurar reglas de acceso
- Consultar auditoría y reportes
- Investigar incidentes

**Permisos**:
- Acceso completo a reportes y auditoría
- Gestión de autorizaciones especiales

### 3.5. RRHH (Recursos Humanos)
**Descripción**: Personal de recursos humanos que gestiona altas/bajas de empleados.

**Responsabilidades**:
- Registrar nuevos empleados
- Actualizar información de empleados
- Desactivar empleados (bajas)

**Permisos**:
- Crear y editar registros de empleados
- Cambiar estado de empleados (activo/inactivo)
- Consultar información de empleados

### 3.6. Sistema de Torniquetes/Control Físico
**Descripción**: Dispositivo físico que valida acceso y controla el paso de personas.

**Responsabilidades**:
- Leer credenciales (tarjeta, QR, biometría)
- Consultar al sistema si el acceso es permitido
- Desbloquear/bloquear según respuesta
- Registrar eventos de acceso

**Características**:
- Integración mediante API REST
- Respuesta en tiempo real (< 2 segundos)

---

## 4. Requerimientos Funcionales

### RF-01 – Registro de Personas

**Prioridad**: Alta

**Descripción**:  
El sistema debe permitir registrar personas (empleados propios, empleados externos o visitantes temporales) con la siguiente información:
- Tipo de persona (visitante temporal, empleado propio, empleado externo)
- Nombre completo
- Número de documento de identidad
- Teléfono y email (opcional)
- Empresa (para empleados externos o visitantes)
- Cargo y área (opcional)
- Estado (activo/inactivo)
- **Foto facial (OBLIGATORIA)**: Para generar embedding de reconocimiento facial

**Precondiciones**:
- Usuario autenticado con rol de RRHH, Recepción o Administrador
- Información básica de la persona disponible
- Foto facial disponible (captura en tiempo real o archivo)

**Postcondiciones**:
- Persona registrada en el sistema
- Embedding facial generado y almacenado automáticamente (MVP: librería pre-entrenada como face_recognition, DeepFace o MediaPipe; ver 08-definicion-proyecto.md)
- Embedding validado (calidad mínima configurable)
- Si es empleado: autorización automática generada por RRHH
- Si es visitante: disponible para generar autorización

**Casos de Uso Relacionados**: HU-01

---

### RF-01A – Registro de Reconocimiento Facial

**Prioridad**: Alta

**Descripción**:  
El sistema debe generar automáticamente el embedding facial de una persona al momento del registro. **Para el MVP** se usan librerías pre-entrenadas (face_recognition, DeepFace o MediaPipe):
- Captura o carga de foto facial de referencia (obligatoria en el registro)
- Detección de rostro usando la librería pre-entrenada
- Generación de embedding (dimensiones según librería)
- Almacenamiento del embedding en la base de datos
- Validación de calidad del embedding (score mínimo configurable, opcional en MVP)

**Nota**: Este proceso es automático durante el registro. En iteraciones futuras podrían usarse YOLOv8 (detección) y ArcFace (embeddings). Referencia: 08-definicion-proyecto.md.

**Precondiciones**:
- Persona registrada en el sistema (o en proceso de registro)
- Foto facial disponible (captura en tiempo real o archivo)
- Usuario autenticado con rol adecuado

**Postcondiciones**:
- Embedding facial generado y almacenado
- Embedding anterior desactivado (si existe)
- Nuevo embedding marcado como activo
- Score de calidad registrado
- Persona puede ser identificada por reconocimiento facial

**Rendimiento**: 
- Generación de embedding no debe superar 3 segundos
- Detección de rostro no debe superar un tiempo aceptable (MVP: &lt; 10 s total para el flujo; ver 08)

**Casos de Uso Relacionados**: HU-01

---

### RF-02 – Actualización de Estado de Personas

**Prioridad**: Alta

**Descripción**:  
El sistema debe permitir cambiar el estado de una persona (activo/inactivo). Cuando una persona se marca como inactiva, su acceso debe ser bloqueado inmediatamente.

**Precondiciones**:
- Persona existe en el sistema
- Usuario autenticado con rol de RRHH, Recepción o Administrador

**Postcondiciones**:
- Estado de la persona actualizado
- Autorizaciones activas revocadas (si se marca como inactiva)
- Acceso bloqueado inmediatamente

**Casos de Uso Relacionados**: HU-02

---

### RF-03 – Generación de Autorización *(fuera del MVP)*

**Prioridad**: Alta

**Descripción**:  
El sistema debe generar autorizaciones de acceso:
- **Para empleados**: Se genera automáticamente desde RRHH al registrar la persona (puede ser permanente)
- **Para visitantes**: Un empleado registrado debe autorizar, con fecha de inicio y fin

La autorización incluye:
- Fecha de inicio y fin (NULL = permanente para empleados)
- Estado (activa/vencida/revocada)
- Empleado que autoriza (para visitantes)

**Precondiciones**:
- Persona registrada en el sistema
- Usuario autenticado con rol adecuado (RRHH para empleados, Recepción/Empleado para visitantes)

**Postcondiciones**:
- Autorización generada y activa
- Persona puede ingresar en el periodo autorizado

**Casos de Uso Relacionados**: HU-03, HU-04

---

### RF-04 – Validación de Acceso en Puerta Principal por Reconocimiento Facial

**Prioridad**: Crítica

**Descripción**:  
El sistema debe validar el acceso por la puerta principal **principalmente mediante reconocimiento facial**. El proceso incluye:
- **Identificación por reconocimiento facial** (método principal). **MVP**: librerías pre-entrenadas (face_recognition, DeepFace, MediaPipe):
  - Captura de imagen (en tiempo real o archivo)
  - Detección de rostro y generación de embedding con la librería pre-entrenada
  - Comparación con embeddings almacenados (similaridad coseno o distancia euclidiana)
  - Umbral de confianza configurable (ej. 0.7)
- **Validación**: Una vez identificada la persona:
  - Verificar que está registrada y en estado activo
  - **MVP**: no se verifica autorización (todas las personas activas tienen acceso); en iteraciones futuras: autorización vigente (fecha inicio/fin)

**Método alternativo por documento**: Fuera del MVP; en futuras iteraciones se podría validar por documento.

Debe responder "permitir" o "denegar" con el motivo en caso de denegación.

**Precondiciones**:
- Cámara activa y funcionando
- Imagen capturada en tiempo real
- Sistema de reconocimiento facial operativo

**Postcondiciones**:
- Respuesta de validación generada
- Registro de acceso creado (permitido o denegado)
- Score de similaridad registrado
- Método de identificación registrado (reconocimiento facial o documento)

**Rendimiento**: 
- **MVP**: Validación por reconocimiento facial en tiempo aceptable (&lt; 10 segundos; ver 08-definicion-proyecto.md). Iteraciones futuras: objetivo &lt; 4 s.
- Validación por documento (alternativa): fuera del MVP

**Casos de Uso Relacionados**: HU-05A

---

### RF-05 – Registro de Ingresos y Salidas

**Prioridad**: Alta

**Descripción**:  
El sistema debe registrar cada ingreso y salida por la puerta principal con la siguiente información:
- Persona (ID)
- Tipo de movimiento (ingreso/salida)
- Fecha y hora
- Resultado (permitido/denegado)
- Motivo de denegación (si aplica)
- Observaciones (opcional)

**Precondiciones**:
- Solicitud de acceso recibida
- Validación realizada

**Postcondiciones**:
- Registro de acceso creado en el sistema
- Disponible para consultas y auditoría

**Casos de Uso Relacionados**: HU-06, HU-07

---

### RF-06 – Consulta de Historial de Accesos

**Prioridad**: Media

**Descripción**:  
El sistema debe permitir consultar el historial de accesos (auditoría) con filtros por:
- Persona (por nombre o documento)
- Fecha (rango)
- Tipo de movimiento (ingreso/salida)
- Resultado (permitido/denegado)

**Precondiciones**:
- Usuario autenticado con permisos de consulta
- Datos históricos disponibles

**Postcondiciones**:
- Resultados de consulta mostrados
- Opción de exportar resultados (opcional)

**Casos de Uso Relacionados**: HU-08

---

### RF-07 – Gestión de Usuarios del Sistema

**Prioridad**: Media

**Descripción**:  
El sistema debe permitir gestionar usuarios administrativos (RRHH, Recepción, Seguridad) con:
- Nombre de usuario
- Contraseña (hash seguro)
- Rol asignado (admin, rrhh, recepcion, seguridad)
- Persona asociada (opcional, si es empleado)
- Estado (activo/inactivo)

**Precondiciones**:
- Usuario autenticado con rol de Administrador

**Postcondiciones**:
- Usuario creado/actualizado
- Permisos aplicados según rol

**Casos de Uso Relacionados**: HU-09

---

## 5. Requerimientos No Funcionales

### RNF-01 – Seguridad

**Prioridad**: Crítica

**Descripción**:  
El sistema debe implementar medidas de seguridad adecuadas:

- **Autenticación**: Todos los usuarios deben autenticarse antes de acceder al sistema
- **Autorización**: Control de acceso basado en roles (RBAC)
- **Cifrado**: Datos sensibles cifrados en tránsito (HTTPS/TLS) y en reposo
- **Gestión de contraseñas**: Almacenamiento seguro (hashing con salt), políticas de complejidad
- **Auditoría**: Registro de todas las acciones críticas de usuarios administrativos
- **Protección contra ataques**: Prevención de SQL injection, XSS, CSRF

**Criterios de Aceptación**:
- Autenticación requerida para todas las operaciones
- Contraseñas almacenadas con hash seguro (bcrypt, Argon2)
- Comunicación cifrada (TLS 1.2+)
- Logs de auditoría inmutables

---

### RNF-02 – Disponibilidad

**Prioridad**: Alta

**Descripción**:  
El sistema debe estar disponible durante los horarios de operación de la empresa.

- **Horario mínimo**: 7x12 (7 días a la semana, 12 horas al día)
- **Horario objetivo**: 24/7 para validación de acceso
- **Tiempo de inactividad planificado**: Máximo 4 horas/mes para mantenimiento

**Criterios de Aceptación**:
- Disponibilidad mínima del 99% durante horario laboral
- Tiempo de recuperación (RTO): Máximo 1 hora
- Punto de recuperación (RPO): Máximo 15 minutos

---

### RNF-03 – Rendimiento

**Prioridad**: Crítica

**Descripción**:  
El sistema debe responder en tiempos adecuados según el tipo de operación:

- **Validación de acceso**: No debe superar 2 segundos desde la lectura de credencial hasta la respuesta
- **Consultas de historial**: Respuesta en menos de 5 segundos para consultas estándar
- **Carga de página**: Interfaz web debe cargar en menos de 3 segundos

**Criterios de Aceptación**:
- 95% de las validaciones de acceso en menos de 2 segundos
- Consultas de historial responden en menos de 5 segundos (hasta 10,000 registros)
- Interfaz web carga en menos de 3 segundos

---

### RNF-04 – Trazabilidad

**Prioridad**: Alta

**Descripción**:  
Todos los cambios de configuración y datos críticos deben quedar auditados:

- Registro de quién realizó la acción
- Fecha y hora de la acción
- Detalle de la acción realizada
- Estado anterior y nuevo (para modificaciones)

**Criterios de Aceptación**:
- Todos los eventos de acceso registrados
- Todas las modificaciones de datos críticos auditadas
- Logs inmutables y con integridad verificable

---

### RNF-05 – Escalabilidad

**Prioridad**: Media

**Descripción**:  
El sistema debe ser capaz de crecer según las necesidades:

- Soporte para al menos 1,000 empleados
- Soporte para al menos 100 visitantes simultáneos
- Soporte para al menos 10 puntos de acceso
- Almacenamiento de al menos 5 años de historial

**Criterios de Aceptación**:
- Sistema funciona correctamente con 1,000 empleados registrados
- Soporta 100 validaciones simultáneas sin degradación
- Almacenamiento escalable para 5 años de datos

---

### RNF-06 – Usabilidad

**Prioridad**: Media

**Descripción**:  
El sistema debe ser fácil de usar:

- Interfaz intuitiva y clara
- Tiempo de aprendizaje mínimo
- Documentación de usuario disponible
- Soporte para múltiples idiomas (español como principal)

**Criterios de Aceptación**:
- Usuarios pueden realizar tareas básicas sin capacitación
- Interfaz responsive (móvil y escritorio)
- Documentación disponible en línea

---

### RNF-07 – Mantenibilidad

**Prioridad**: Media

**Descripción**:  
El sistema debe ser fácil de mantener:

- Código bien documentado
- Arquitectura modular
- Logs detallados para debugging
- Documentación técnica actualizada

**Criterios de Aceptación**:
- Código con comentarios y documentación
- Arquitectura documentada
- Logs estructurados y consultables

---

## 6. Restricciones del Sistema

### 6.1. Restricciones Técnicas

- El sistema debe integrarse con dispositivos físicos existentes (torniquetes, lectores)
- Debe funcionar en navegadores modernos (Chrome, Firefox, Edge - últimas 2 versiones)
- Debe ser compatible con sistemas operativos Windows y Linux para servidores

### 6.2. Restricciones de Negocio

- Debe cumplir con políticas de seguridad de STI S.A.S.
- Debe respetar normativas de protección de datos personales
- Debe ser implementado sin interrumpir operaciones actuales

### 6.3. Restricciones de Implementación

- Presupuesto limitado (definido en caso de negocio)
- Tiempo de implementación: 6 meses
- Recursos técnicos disponibles limitados

---

## 7. Supuestos y Dependencias

### 7.1. Supuestos

- Los dispositivos físicos (torniquetes) tienen capacidad de comunicación con APIs REST
- Existe conectividad de red entre dispositivos y servidor del sistema
- Los usuarios tienen acceso a navegadores web modernos
- Existe personal técnico para mantenimiento del sistema

### 7.2. Dependencias

- Infraestructura de red estable
- Servidores con capacidad suficiente
- Base de datos relacional (PostgreSQL, MySQL, SQL Server)
- Servicios de autenticación (opcional: LDAP, Active Directory)

---

**Documento**: Especificación de Requerimientos (SRS)  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
