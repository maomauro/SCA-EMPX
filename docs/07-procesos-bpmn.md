# 🔄 Procesos BPMN - Flujos de Negocio

## 1. Introducción

Este documento describe los **procesos de negocio** del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** utilizando notación BPMN (Business Process Model and Notation).

**Alcance MVP:** Para el MVP (ver [08-definicion-proyecto.md](./08-definicion-proyecto.md)) se utilizan **librerías pre-entrenadas** (face_recognition, DeepFace o MediaPipe) para detección y embedding; no se implementa validación de autorizaciones (todas las personas activas tienen acceso) ni integración con torniquetes. Los pasos que mencionan YOLOv8/ArcFace o "desbloquear torniquete" aplican a iteraciones futuras o se indican como fuera del MVP.

Los procesos están descritos de forma textual y estructurada para facilitar su comprensión e implementación.

---

## 2. Proceso Principal: Ingreso a la Empresa por Reconocimiento Facial

### 2.1. Descripción General

Este proceso describe el flujo completo desde que una persona se presenta en el punto de acceso hasta que se registra su entrada o se deniega el acceso. **El método principal de identificación es el reconocimiento facial**.

**Actor Principal**: Persona (Empleado o Visitante)  
**Actor Secundario**: Sistema de Control de Acceso + Sistema de Reconocimiento Facial  
**Disparador**: Persona se presenta frente a la cámara en el punto de acceso

---

### 2.2. Flujo Detallado del Proceso

#### **Paso 1: Inicio del Proceso**

**Actividad**: Persona se presenta frente a la cámara en el punto de acceso

**Condición**: Cámara activa y funcionando

**Resultado**: Proceso inicia

---

#### **Paso 2: Captura de Imagen**

**Actividad**: La cámara captura imagen en tiempo real automáticamente

**Resultado**: Imagen capturada

**Excepciones**:
- Si la imagen no se puede capturar → Mostrar error "Error de cámara" → Fin del proceso

---

#### **Paso 3: Enviar Solicitud de Reconocimiento**

**Actividad**: El sistema envía imagen al servicio de reconocimiento facial

**Datos Enviados**:
```json
{
  "image": "base64_encoded_image",
  "timestamp": "2024-01-15T10:30:00"
}
```

**Protocolo**: HTTP POST a `/api/v1/access/validate-face`

**Resultado**: Solicitud recibida

**Excepciones**:
- Si no hay conectividad → Mostrar error "Sistema no disponible" → Fin del proceso
- Si timeout (> 5 segundos) → Mostrar error "Tiempo de espera agotado" → Fin del proceso

---

#### **Paso 4: Detección de Rostro**

**Actividad**: El servicio de reconocimiento facial detecta rostro en la imagen (MVP: librería pre-entrenada, p. ej. face_recognition, DeepFace o MediaPipe; futuras iteraciones podrían usar YOLOv8).

**Validación**:
- Usar modelo de detección de rostros (pre-entrenado en MVP)
- Verificar que se detectó exactamente un rostro

**Decisión**: ¿Se detectó un rostro?

**NO** → 
- **Respuesta**: Acceso denegado
- **Motivo**: "Rostro no detectado" o "Múltiples rostros detectados"
- **Acción**: Registrar evento de acceso denegado
- **Fin del proceso**

**SÍ** → Continuar al siguiente paso

---

#### **Paso 5: Generación de Embedding**

**Actividad**: El sistema genera embedding facial (MVP: misma librería pre-entrenada; futuras iteraciones podrían usar ArcFace).

**Proceso**:
- Extraer región del rostro detectado
- Generar embedding (dimensiones según librería; ej. 128 en face_recognition)
- Calcular score de calidad del embedding (opcional en MVP)

**Resultado**: Embedding generado

**Excepciones**:
- Si la calidad es muy baja → Denegar acceso → Fin del proceso

---

#### **Paso 6: Comparación con Embeddings Almacenados**

**Actividad**: El sistema compara el embedding con los almacenados

**Proceso**:
- Obtener todos los embeddings activos de la BD
- Calcular similaridad coseno con cada embedding
- Encontrar el embedding con mayor similaridad
- Verificar si supera el umbral (ej. 0.7)

**Decisión**: ¿Se encontró coincidencia con similarity > umbral?

**NO** → 
- **Respuesta**: Acceso denegado
- **Motivo**: "Persona no identificada"
- **Acción**: Registrar evento de acceso denegado
- **Fin del proceso**

**SÍ** → Continuar al siguiente paso

---

#### **Paso 7: Validar Persona Identificada**

**Actividad**: El sistema valida la persona identificada

**Validación**:
- Obtener datos de la persona por ID
- Verificar que `estado = 'activo'`

**Decisión**: ¿La persona está activa?

**NO** → 
- **Respuesta**: Acceso denegado
- **Motivo**: "Persona inactiva"
- **Acción**: Registrar evento de acceso denegado
- **Fin del proceso**

**SÍ** → Continuar al siguiente paso

---

#### **Paso 7: Validar Autorización Vigente** *(fuera del MVP)*

**Actividad**: En iteraciones futuras el sistema verifica autorización vigente. **En MVP se omite**: todas las personas activas tienen acceso.

**Validación** (solo en iteraciones futuras):
1. Buscar en tabla `autorizacion`:
   - `id_persona` = ID de la persona
   - `estado = 'activa'`
   - `fecha_inicio <= timestamp actual`
   - `fecha_fin IS NULL OR fecha_fin >= timestamp actual`

2. Verificar que existe al menos una autorización que cumpla todas las condiciones

**Decisión**: ¿Existe autorización vigente?

**NO** → 
- **Respuesta**: Acceso denegado
- **Motivo**: "Sin autorización vigente"
- **Acción**: Registrar evento de acceso denegado
- **Fin del proceso**

**SÍ** → Continuar al siguiente paso

---

#### **Paso 8: Permitir Acceso**

**Actividad**: El sistema responde con acceso permitido

**Respuesta al Dispositivo**:
```json
{
  "allowed": true,
  "person_id": 123,
  "person_name": "Juan Pérez",
  "message": "Acceso permitido"
}
```

**Acción del Dispositivo**:
- Desbloquear torniquete/puerta (fuera del MVP)
- Mostrar mensaje de bienvenida (opcional)
- Permitir el paso

**Resultado**: Acceso permitido físicamente

---

#### **Paso 9: Registrar Evento de Entrada**

**Actividad**: El sistema registra el evento de acceso exitoso

**Registro en BD**:
- Insertar en tabla `evento_acceso`:
  - `id_persona`: ID de la persona
  - `id_punto_acceso`: ID del punto de acceso
  - `tipo_evento`: 'entrada'
  - `resultado`: 'permitido'
  - `fecha_hora`: Timestamp del evento
  - `credencial_usada`: ID de la credencial utilizada

**Nota**: Este registro es **inmutable** (no se puede modificar ni eliminar)

**Resultado**: Evento registrado en el sistema

---

#### **Paso 10: Fin del Proceso de Ingreso**

**Actividad**: Proceso completado exitosamente

**Estado Final**: 
- Persona dentro de las instalaciones
- Evento de entrada registrado
- Disponible para consultas y reportes

---

### 2.3. Diagrama de Flujo (Descripción Textual)

```
[INICIO]
    ↓
[Persona se presenta frente a la cámara]
    ↓
[Cámara captura imagen]
    ↓
[Enviar solicitud de reconocimiento]
    ↓
[¿Rostro detectado?] ──NO──→ [Denegar: "Rostro no detectado"] → [Registrar evento] → [FIN]
    ↓ SÍ
[Generar embedding] (MVP: librería pre-entrenada)
    ↓
[Comparar con embeddings almacenados]
    ↓
[¿Coincidencia encontrada?] ──NO──→ [Denegar: "Persona no identificada"] → [Registrar evento] → [FIN]
    ↓ SÍ (similarity > 0.7)
[¿Persona activa?] ──NO──→ [Denegar: "Persona inactiva"] → [Registrar evento] → [FIN]
    ↓ SÍ
[¿Autorización vigente?] ──NO──→ [Denegar: "Sin autorización"] → [Registrar evento] → [FIN]
    ↓ SÍ
[Permitir acceso]
    ↓
[Desbloquear torniquete] (fuera del MVP)
    ↓
[Registrar evento de entrada (con similarity)]
    ↓
[FIN - Persona dentro]
```

---

## 3. Proceso Alternativo: Ingreso por Documento

### 3.1. Descripción General

Este proceso describe el flujo alternativo cuando una persona ingresa usando documento (solo cuando el reconocimiento facial no está disponible o falla).

**Actor Principal**: Persona (Empleado o Visitante)  
**Actor Secundario**: Sistema de Control de Acceso  
**Disparador**: Persona presenta documento en punto de acceso

---

### 3.2. Flujo Detallado del Proceso

#### **Paso 1: Inicio del Proceso (Alternativo)**

**Actividad**: Persona se presenta en el punto de acceso con documento

**Condición**: Reconocimiento facial no disponible o falló

**Resultado**: Proceso inicia

---

#### **Paso 2: Lectura de Documento**

**Actividad**: El sistema lee el número de documento (escaneo o ingreso manual)

**Resultado**: Documento capturado

---

#### **Paso 3: Enviar Solicitud de Validación**

**Actividad**: El sistema envía solicitud de validación por documento

**Datos Enviados**:
```json
{
  "document": "12345678",
  "timestamp": "2024-01-15T10:30:00"
}
```

**Protocolo**: HTTP POST a `/api/v1/access/validate-document`

**Resultado**: Solicitud recibida

---

#### **Paso 4: Buscar Persona por Documento**

**Actividad**: El sistema busca la persona por documento

**Validación**:
- Buscar en tabla `persona` por `documento`
- Verificar que existe

**Decisión**: ¿Existe la persona?

**NO** → 
- **Respuesta**: Acceso denegado
- **Motivo**: "Persona no registrada"
- **Acción**: Registrar evento de acceso denegado
- **Fin del proceso**

**SÍ** → Continuar al siguiente paso

---

#### **Paso 5: Validar Estado de Persona**

**Actividad**: El sistema verifica el estado de la persona

**Validación**:
- Consultar campo `estado` en tabla `persona`
- Verificar que `estado = 'activo'`

**Decisión**: ¿La persona está activa?

**NO** → 
- **Respuesta**: Acceso denegado
- **Motivo**: "Persona inactiva"
- **Acción**: Registrar evento de acceso denegado
- **Fin del proceso**

**SÍ** → Continuar al siguiente paso

---

#### **Paso 6: Validar Autorización Vigente**

**Actividad**: El sistema verifica autorización vigente

**Validación**:
- Buscar autorización activa
- Verificar fechas de vigencia

**Decisión**: ¿Existe autorización vigente?

**NO** → 
- **Respuesta**: Acceso denegado
- **Motivo**: "Sin autorización vigente"
- **Acción**: Registrar evento de acceso denegado
- **Fin del proceso**

**SÍ** → Continuar al siguiente paso

---

#### **Paso 7: Permitir Acceso**

**Actividad**: El sistema responde con acceso permitido

**Respuesta**:
```json
{
  "allowed": true,
  "person_id": 123,
  "person_name": "Juan Pérez",
  "message": "Acceso permitido"
}
```

**Acción del Dispositivo**:
- Desbloquear torniquete/puerta (fuera del MVP)
- Mostrar mensaje de bienvenida
- Permitir el paso

---

#### **Paso 8: Registrar Evento de Entrada**

**Actividad**: El sistema registra el evento

**Registro en BD**:
- Insertar en tabla `registro_acceso`:
  - `id_persona`: ID de la persona
  - `tipo_movimiento`: 'ingreso'
  - `metodo_identificacion`: 'documento'
  - `resultado`: 'permitido'
  - `fecha_hora`: Timestamp del evento

**Resultado**: Evento registrado

---

#### **Paso 9: Fin del Proceso**

**Actividad**: Proceso completado exitosamente

**Estado Final**: 
- Persona dentro de las instalaciones
- Evento de entrada registrado

---

## 4. Proceso: Salida de la Empresa por Reconocimiento Facial

### 4.1. Descripción General

Este proceso describe el flujo cuando una persona sale de las instalaciones. **El método principal de identificación es el reconocimiento facial**.

**Actor Principal**: Persona (Empleado o Visitante)  
**Actor Secundario**: Sistema de Control de Acceso + Sistema de Reconocimiento Facial  
**Disparador**: Persona se presenta frente a la cámara en punto de salida

---

### 4.2. Flujo Detallado del Proceso

#### **Paso 1: Inicio del Proceso**

**Actividad**: Persona se presenta frente a la cámara en el punto de salida

**Condición**: Cámara activa y funcionando

**Resultado**: Proceso inicia

---

#### **Paso 2: Captura de Imagen**

**Actividad**: La cámara captura imagen en tiempo real

**Resultado**: Imagen capturada

---

#### **Paso 3: Identificación por Reconocimiento Facial**

**Actividad**: El sistema identifica a la persona usando reconocimiento facial

**Proceso** (simplificado para salida):
- Detección de rostro (MVP: pre-entrenado)
- Generación de embedding (MVP: pre-entrenado)
- Comparación con embeddings almacenados
- Identificación de persona si similarity > umbral

**Decisión**: ¿Se identificó a la persona?

**NO** → 
- **Respuesta**: Salida permitida (validación laxa para salida)
- **Acción**: Registrar evento de salida sin identificación
- **Fin del proceso**

**SÍ** → Continuar

**Nota**: Para salida, la validación es más laxa. Si no se identifica, igual se permite la salida (pero se registra).

---

#### **Paso 4: Permitir Salida**

**Actividad**: El sistema responde con salida permitida

**Respuesta**:
```json
{
  "allowed": true,
  "person_id": 123,
  "person_name": "Juan Pérez",
  "similarity": 0.85,
  "message": "Salida permitida"
}
```

**Acción del Dispositivo**:
- Desbloquear torniquete/puerta automáticamente (fuera del MVP)
- Permitir el paso

---

#### **Paso 5: Registrar Evento de Salida**

**Actividad**: El sistema registra el evento de salida

**Registro en BD**:
- Insertar en tabla `registro_acceso`:
  - `id_persona`: ID de la persona (si fue identificada)
  - `tipo_movimiento`: 'salida'
  - `metodo_identificacion`: 'reconocimiento_facial' o 'no_identificado'
  - `resultado`: 'permitido'
  - `fecha_hora`: Timestamp del evento
  - `similarity_score`: Score de similaridad (si fue identificada)

**Resultado**: Evento registrado

---

#### **Paso 6: Fin del Proceso de Salida**

**Actividad**: Proceso completado

**Estado Final**: 
- Persona fuera de las instalaciones
- Evento de salida registrado
- Disponible para consultas

---

### 4.3. Diagrama de Flujo (Descripción Textual)

```
[INICIO]
    ↓
[Persona se presenta frente a la cámara]
    ↓
[Cámara captura imagen]
    ↓
[Identificación por reconocimiento facial]
    ↓
[Permitir salida (siempre permitida)]
    ↓
[Desbloquear torniquete] (fuera del MVP)
    ↓
[Registrar evento de salida]
    ↓
[FIN - Persona fuera]
```

---

## 4. Proceso: Registro de Visitante

### 4.1. Descripción General

Este proceso describe cómo un recepcionista registra un visitante y genera su autorización.

**Actor Principal**: Recepcionista  
**Actor Secundario**: Sistema SCA-EMPX  
**Disparador**: Visitante llega a recepción

---

### 4.2. Flujo Detallado

1. **Recepcionista accede al sistema** (autenticación)
2. **Recepcionista completa formulario de visitante**:
   - Nombre completo
   - Documento
   - Empresa (opcional)
   - Persona a quien visita (empleado)
   - Motivo de visita
   - **Foto facial (OBLIGATORIA)**: Captura o carga de imagen
3. **Sistema valida datos** (documento único, empleado existe)
4. **Sistema crea registro de visitante** en tabla `persona` (tipo: visitante_temporal)
5. **Sistema genera embedding facial automáticamente**:
   - Detecta rostro (MVP: pre-entrenado)
   - Genera embedding (MVP: pre-entrenado)
   - Almacena en tabla `reconocimiento_facial`
6. **Recepcionista o empleado define autorización**:
   - Fecha y hora de inicio
   - Fecha y hora de fin
   - Empleado que autoriza
7. (Fuera del MVP) **Sistema crea autorización** en tabla `autorizacion`. En MVP no se implementa.
8. **Fin**: Visitante puede ingresar usando reconocimiento facial en el rango de fechas autorizado

---

## 5. Proceso: Desactivación de Empleado

### 5.1. Descripción General

Este proceso describe cómo RRHH desactiva un empleado y se bloquea su acceso.

**Actor Principal**: Analista de RRHH  
**Actor Secundario**: Sistema SCA-EMPX  
**Disparador**: Empleado sale de la empresa o se requiere bloquear acceso

---

### 5.2. Flujo Detallado

1. **RRHH accede al sistema** (autenticación)
2. **RRHH busca empleado** (por nombre o documento)
3. **RRHH cambia estado a "inactivo"**
4. **Sistema valida cambio**
5. (Fuera del MVP) **Sistema revoca autorizaciones**. En MVP: solo se desactiva la persona (estado inactivo).
   - En iteraciones futuras: actualiza `estado = 'revocada'` en tabla `autorizacion`
   - Registra motivo: "Empleado desactivado"
6. **Sistema desactiva el embedding facial**:
   - Actualiza `estado = 'inactivo'` en tabla `reconocimiento_facial`
7. **Sistema registra en log de auditoría**
8. **Sistema confirma desactivación**
9. **Fin**: Empleado no puede acceder (validaciones futuras denegadas, reconocimiento facial no funcionará)

---

## 6. Reglas de Negocio en los Procesos

### 6.1. Reglas de Validación de Acceso

1. **Orden de validación (reconocimiento facial)**: Detección → Embedding → Identificación → Estado → Autorización
2. **Tiempo máximo de respuesta**: 4 segundos para reconocimiento facial completo
3. **Método principal**: Reconocimiento facial (obligatorio para todos)
4. **Método alternativo**: Documento (solo cuando reconocimiento facial no está disponible)
3. **Registro obligatorio**: Todos los intentos (permitidos o denegados) se registran
4. **Inmutabilidad**: Los eventos registrados no se pueden modificar ni eliminar

### 6.2. Reglas de Autorización

1. **Autorización permanente**: Empleados tienen autorización sin `fecha_fin` (NULL)
2. **Autorización temporal**: Visitantes tienen autorización con `fecha_fin` definida
3. **Validación por fecha**: Se valida que la fecha actual esté entre `fecha_inicio` y `fecha_fin` (o `fecha_fin` sea NULL)

### 6.3. Reglas de Salida

1. **Validación simplificada**: Solo verifica que la persona existe
2. **No requiere autorización vigente**: Cualquier persona registrada puede salir
3. **Registro obligatorio**: Todas las salidas se registran

---

## 7. Excepciones y Manejo de Errores

### 7.1. Errores de Conectividad

- **Sistema no disponible**: Dispositivo muestra mensaje y permite reintento
- **Timeout**: Después de 5 segundos, considerar fallo y mostrar error

### 7.2. Errores de Validación

- **Persona no encontrada**: Denegar acceso, registrar evento
- **Credencial inválida**: Denegar acceso, registrar evento
- **Sin autorización**: Denegar acceso, registrar evento con motivo específico

### 7.3. Errores del Sistema

- **Error de base de datos**: Registrar en log, denegar acceso por seguridad
- **Error de aplicación**: Registrar en log, denegar acceso por seguridad

---

## 8. Métricas del Proceso

### 8.1. Métricas de Rendimiento

- **Tiempo promedio de validación**: < 2 segundos
- **Tasa de éxito de validaciones**: > 95%
- **Tasa de denegaciones**: Según políticas de seguridad

### 8.2. Métricas de Negocio

- **Total de accesos por día**: Para análisis de ocupación
- **Horarios pico**: Para optimización de recursos
- **Tasa de visitantes vs empleados**: Para análisis de tráfico

---

**Documento**: Procesos BPMN - Flujos de Negocio  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
