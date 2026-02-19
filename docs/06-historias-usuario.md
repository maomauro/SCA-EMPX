# 👥 Historias de Usuario y Backlog Ágil

## 1. Introducción

Este documento contiene las **Historias de Usuario** del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** organizadas en formato ágil para gestión de backlog.

**Alcance MVP:** El MVP (3 semanas) está definido en [08-definicion-proyecto.md](./08-definicion-proyecto.md). En el MVP se usan **librerías pre-entrenadas** (face_recognition, DeepFace o MediaPipe) para reconocimiento facial; no se implementan autorizaciones complejas ni integración con torniquetes. Las historias marcadas como *Fuera del MVP* o que mencionan YOLOv8/ArcFace corresponden a iteraciones futuras.

Las historias están priorizadas y agrupadas por épicas y funcionalidades principales.

---

## 2. Formato de Historias de Usuario

Cada historia de usuario sigue el formato estándar:

```
Como [rol/usuario]
Quiero [acción/funcionalidad]
Para [beneficio/objetivo]

Criterios de Aceptación:
- [Criterio 1]
- [Criterio 2]
- [Criterio 3]

Prioridad: [Alta/Media/Baja]
Estimación: [Story Points]
```

---

## 3. Épicas

### Épica 1: Gestión de Personas
Gestión de empleados y visitantes del sistema.

### Épica 2: Control de Acceso
Validación y registro de accesos en tiempo real.

### Épica 3: Autorizaciones *(fuera del MVP; iteraciones futuras)*
Gestión de permisos y autorizaciones de acceso. En MVP todas las personas activas tienen acceso.

### Épica 4: Auditoría y Reportes
Consultas, reportes y análisis de accesos.

### Épica 5: Administración
Configuración del sistema y usuarios.

---

## 4. Historias de Usuario

### HU-01 – Registrar Empleado

**Como** analista de RRHH  
**Quiero** registrar un nuevo empleado con sus datos y credencial de acceso  
**Para** que pueda ingresar a las instalaciones de la empresa.

**Criterios de Aceptación**:
- Puedo ingresar nombre completo, documento, cargo, área y tipo de contrato
- El sistema valida que el documento no esté duplicado
- **DEBO capturar o cargar foto facial del empleado (OBLIGATORIO)**
- El sistema detecta automáticamente el rostro (MVP: modelo pre-entrenado, p. ej. face_recognition, DeepFace o MediaPipe)
- El sistema genera embedding facial automáticamente
- El sistema valida la calidad del embedding (score mínimo; opcional en MVP)
- Si la calidad es insuficiente: el sistema solicita nueva foto
- (Fuera del MVP) Autorización permanente. En MVP el empleado activo tiene acceso por defecto.
- El empleado queda en estado "activo" por defecto
- Recibo confirmación de registro exitoso con score de calidad del embedding

**Prioridad**: Alta  
**Estimación**: 5 puntos  
**Épica**: Gestión de Personas  
**Requerimiento**: RF-01

---

### HU-02 – Desactivar Empleado

**Como** analista de RRHH  
**Quiero** cambiar el estado de un empleado a inactivo  
**Para** impedir que siga ingresando a la empresa.

**Criterios de Aceptación**:
- Puedo buscar un empleado por nombre o documento
- Puedo cambiar el estado de "activo" a "inactivo"
- (En iteraciones futuras: revocar autorizaciones). En MVP: al desactivar, el sistema bloquea el acceso (persona inactiva).
- El sistema bloquea el acceso inmediatamente (validaciones futuras denegadas)
- Recibo confirmación de desactivación
- El historial de accesos se mantiene intacto

**Prioridad**: Alta  
**Estimación**: 3 puntos  
**Épica**: Gestión de Personas  
**Requerimiento**: RF-02

---

### HU-03 – Registrar Visitante

**Como** recepcionista  
**Quiero** registrar los datos de un visitante y la persona a quien visita  
**Para** generar una autorización de ingreso controlada.

**Criterios de Aceptación**:
- Puedo ingresar nombre completo, documento, empresa y motivo de visita
- Puedo seleccionar el empleado a quien visita desde una lista
- El sistema valida que el documento no esté duplicado (o permite reutilizar registro existente)
- **DEBO capturar o cargar foto facial del visitante (OBLIGATORIO)**
- El sistema detecta automáticamente el rostro (MVP: modelo pre-entrenado)
- El sistema genera embedding facial automáticamente
- Puedo registrar visitantes de forma rápida (< 2 minutos)
- Recibo confirmación con score de calidad del embedding

**Prioridad**: Alta  
**Estimación**: 5 puntos  
**Épica**: Gestión de Personas  
**Requerimiento**: RF-03

---

### HU-04 – Generar Autorización de Visita

**Como** recepcionista  
**Quiero** generar una autorización con fecha y horario para un visitante  
**Para** que solo pueda ingresar en el periodo permitido.

**Criterios de Aceptación**:
- Puedo seleccionar un visitante registrado
- Puedo definir fecha de inicio y fin de la autorización
- Puedo definir horario de inicio y fin (opcional)
- El sistema valida que las fechas sean coherentes
- La autorización queda en estado "activa"
- Puedo ver un resumen de la autorización generada

**Prioridad**: Alta  
**Estimación**: 5 puntos  
**Épica**: Autorizaciones  
**Requerimiento**: RF-04

---

### HU-05 – Validar Acceso por Reconocimiento Facial (Método Principal)

**Como** sistema de control de acceso  
**Quiero** identificar y validar a una persona mediante reconocimiento facial  
**Para** permitir o denegar el acceso de forma automática y segura.

**Criterios de Aceptación**:
- La cámara (o carga de imagen) proporciona imagen para validación
- El sistema detecta el rostro (MVP: modelo pre-entrenado, p. ej. face_recognition, DeepFace o MediaPipe)
- El sistema genera embedding y compara con embeddings almacenados (similaridad coseno o distancia euclidiana)
- Si encuentra coincidencia (similarity > umbral, ej. 0.7): identifica a la persona
- El sistema valida que la persona está activa (MVP: no se valida autorización; en futuro: autorización vigente)
- **MVP**: El proceso completo en tiempo aceptable (&lt; 10 s). Iteraciones futuras: &lt; 4 s.
- Si no encuentra coincidencia: retorna "persona no identificada"
- El sistema retorna "permitido" o "denegado" con motivo (vía API en MVP)
- (Fuera del MVP) Si es permitido, torniquete se desbloquea. En MVP solo respuesta API.
- Si es denegado, se muestra mensaje de error específico
- El score de similaridad se registra en el evento de acceso

**Prioridad**: Crítica  
**Estimación**: 8 puntos  
**Épica**: Control de Acceso  
**Requerimiento**: RF-04, RF-01A

---

### HU-06 – Registrar Evento de Entrada

**Como** sistema  
**Quiero** registrar cada entrada permitida  
**Para** mantener un historial de accesos.

**Criterios de Aceptación**:
- Se registra automáticamente después de una validación exitosa
- Se guarda: persona, punto de acceso, fecha/hora, tipo (entrada), resultado (permitido)
- El registro es inmutable (no se puede modificar ni eliminar)
- El registro queda disponible inmediatamente para consultas
- Se puede asociar la credencial utilizada

**Prioridad**: Alta  
**Estimación**: 3 puntos  
**Épica**: Control de Acceso  
**Requerimiento**: RF-06

---

### HU-07 – Registrar Evento de Salida

**Como** sistema  
**Quiero** registrar la salida de las personas  
**Para** conocer quién se encuentra actualmente dentro de la empresa.

**Criterios de Aceptación**:
- Se registra cuando una persona presenta credencial en punto de salida
- Se guarda: persona, punto de acceso, fecha/hora, tipo (salida), resultado (permitido)
- El registro es inmutable
- Puedo consultar quién está actualmente dentro (entradas sin salida correspondiente)
- La validación de salida es más laxa que la de entrada (solo verifica que la persona existe)

**Prioridad**: Alta  
**Estimación**: 3 puntos  
**Épica**: Control de Acceso  
**Requerimiento**: RF-07

---

### HU-08 – Consultar Historial de Accesos

**Como** administrador de seguridad  
**Quiero** consultar el historial de accesos por persona y fecha  
**Para** realizar auditorías y análisis de incidentes.

**Criterios de Aceptación**:
- Puedo filtrar por persona (nombre o documento)
- Puedo filtrar por rango de fechas
- Puedo filtrar por tipo de evento (entrada/salida)
- Puedo filtrar por resultado (permitido/denegado)
- Los resultados se muestran paginados (máximo 100 por página)
- Puedo exportar los resultados a Excel o CSV
- Los resultados se ordenan por fecha/hora descendente

**Prioridad**: Media  
**Estimación**: 5 puntos  
**Épica**: Auditoría y Reportes  
**Requerimiento**: RF-08

---


### HU-09 – Gestionar Usuarios del Sistema

**Como** administrador del sistema  
**Quiero** crear y asignar roles a usuarios internos  
**Para** controlar quién puede administrar el sistema.

**Criterios de Aceptación**:
- Puedo crear usuarios con nombre de usuario y contraseña
- Puedo asignar roles (admin, seguridad, RRHH, recepcionista)
- Puedo asociar un usuario a un empleado (opcional)
- Puedo activar/desactivar usuarios
- Puedo cambiar contraseñas
- El sistema valida que las contraseñas cumplan políticas de seguridad
- Puedo ver un listado de todos los usuarios con sus roles

**Prioridad**: Media  
**Estimación**: 5 puntos  
**Épica**: Administración  
**Requerimiento**: RF-10

---

### HU-10 – Actualizar Información de Empleado

**Como** analista de RRHH  
**Quiero** actualizar la información de un empleado existente  
**Para** mantener los datos actualizados.

**Criterios de Aceptación**:
- Puedo buscar un empleado por nombre o documento
- Puedo actualizar: nombre, cargo, área, tipo de contrato
- Puedo actualizar información de contacto (email, teléfono)
- Los cambios quedan registrados en log de auditoría
- Recibo confirmación de actualización exitosa

**Prioridad**: Media  
**Estimación**: 3 puntos  
**Épica**: Gestión de Personas

---

### HU-11 – Ver Dashboard de Accesos

**Como** administrador de seguridad  
**Quiero** ver un dashboard con información en tiempo real de accesos  
**Para** monitorear la actividad de la empresa.

**Criterios de Aceptación**:
- Veo accesos en tiempo real (últimos 10 minutos)
- Veo métricas: total de personas dentro, accesos hoy, denegaciones hoy
- Veo gráfico de accesos por hora del día
- Veo lista de personas actualmente dentro de la empresa
- El dashboard se actualiza automáticamente cada 30 segundos

**Prioridad**: Media  
**Estimación**: 8 puntos  
**Épica**: Auditoría y Reportes

---

### HU-12 – Generar Reporte de Accesos

**Como** administrador de seguridad  
**Quiero** generar reportes de accesos con diferentes criterios  
**Para** análisis y presentaciones.

**Criterios de Aceptación**:
- Puedo seleccionar tipo de reporte (diario, semanal, mensual, personalizado)
- Puedo filtrar por persona y fecha
- El reporte incluye: total de accesos, personas únicas, denegaciones, gráficos
- Puedo exportar el reporte a PDF o Excel
- El reporte se genera en menos de 10 segundos
- Puedo programar reportes recurrentes (opcional)

**Prioridad**: Baja  
**Estimación**: 8 puntos  
**Épica**: Auditoría y Reportes

---

### HU-13 – Revocar Autorización

**Como** administrador de seguridad  
**Quiero** revocar una autorización activa  
**Para** bloquear el acceso de una persona inmediatamente.

**Criterios de Aceptación**:
- Puedo buscar autorizaciones activas por persona
- Puedo revocar una autorización con motivo
- Al revocar, el acceso se bloquea inmediatamente
- La autorización queda en estado "revocada"
- El motivo de revocación queda registrado
- Recibo confirmación de revocación

**Prioridad**: Media  
**Estimación**: 3 puntos  
**Épica**: Autorizaciones

---

### HU-14 – Consultar Personas Dentro de la Empresa

**Como** recepcionista o administrador de seguridad  
**Quiero** ver quién está actualmente dentro de la empresa  
**Para** saber quién se encuentra en las instalaciones.

**Criterios de Aceptación**:
- Veo lista de personas que tienen entrada registrada sin salida correspondiente
- La lista muestra: nombre, hora de entrada
- Puedo ver detalles de cada persona
- La lista se actualiza en tiempo real

**Prioridad**: Media  
**Estimación**: 5 puntos  
**Épica**: Auditoría y Reportes

---

## 5. Backlog Priorizado

### Sprint 1 (MVP - Mínimo Producto Viable)

1. **HU-05A** – Validar Acceso por Reconocimiento Facial (Crítica) - **MÉTODO PRINCIPAL**
2. **HU-01** – Registrar Empleado (Alta) - Con reconocimiento facial obligatorio
3. **HU-03** – Registrar Visitante (Alta) - Con reconocimiento facial obligatorio
4. **HU-04** – Generar Autorización de Visita (Alta)
5. **HU-06** – Registrar Evento de Entrada (Alta)
6. **HU-07** – Registrar Evento de Salida (Alta)
7. **HU-09** – Gestionar Usuarios del Sistema (Media)

**Total estimado**: ~35 puntos

**Nota**: El método alternativo por documento queda fuera del alcance del MVP.

### Sprint 2

1. **HU-02** – Desactivar Empleado (Alta)
2. **HU-08** – Consultar Historial de Accesos (Media)
4. **HU-10** – Actualizar Información de Empleado (Media)

**Total estimado**: ~16 puntos

### Sprint 3

1. **HU-11** – Ver Dashboard de Accesos (Media)
2. **HU-13** – Revocar Autorización (Media)
3. **HU-14** – Consultar Personas Dentro (Media)

**Total estimado**: ~16 puntos

### Sprint 4+

1. **HU-12** – Generar Reporte de Accesos (Baja)
2. Otras mejoras y optimizaciones

---

## 6. Definición de Terminado (DoD)

Para que una historia de usuario se considere terminada, debe cumplir:

- ✅ Código desarrollado y revisado
- ✅ Pruebas unitarias escritas y pasando
- ✅ Pruebas de integración (si aplica)
- ✅ Criterios de aceptación cumplidos
- ✅ Documentación actualizada
- ✅ Código desplegado en ambiente de pruebas
- ✅ Aprobado por el Product Owner
- ✅ Sin bugs críticos o de alta prioridad

---

**Documento**: Historias de Usuario y Backlog Ágil  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
