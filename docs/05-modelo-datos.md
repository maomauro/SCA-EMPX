# 🗄️ Modelo de Datos Simplificado

## 1. Introducción

Este documento describe el modelo de datos simplificado del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)**. El modelo está diseñado para ser simple, funcional y fácil de mantener, enfocado en el control de acceso por la puerta principal de la empresa.

**Característica principal**: El sistema utiliza **reconocimiento facial** como método principal de identificación. **Para el MVP** se usan **librerías pre-entrenadas** (face_recognition, DeepFace o MediaPipe); en iteraciones futuras podrían usarse YOLOv8/ArcFace. Todas las personas deben tener su embedding facial registrado en la tabla `reconocimiento_facial`. Las **tablas principales del MVP** son: `persona`, `reconocimiento_facial` y `registro_acceso`; `autorizacion` y `usuario_sistema` corresponden a iteraciones futuras (ver [08-definicion-proyecto.md](./08-definicion-proyecto.md)).

---

## 2. Diagrama Entidad-Relación (Descripción)

### 2.1. Entidades Principales

El modelo de datos simplificado se organiza en las siguientes entidades:

1. **Persona**: Información completa de todas las personas (empleados y visitantes)
2. **TipoPersona**: Tipos de persona (visitante temporal, empleado propio, empleado externo)
3. **ReconocimientoFacial**: Embeddings faciales para reconocimiento (MVP: librería pre-entrenada)
4. **Autorizacion**: Permisos de acceso con vigencia *(fuera del MVP; ver 08-definicion-proyecto.md)*
5. **RegistroAcceso**: Registro de ingresos y salidas (auditoría)
6. **UsuarioSistema**: Usuarios administrativos del sistema

---

## 3. Esquema de Base de Datos

### 3.1. Tabla: `tipo_persona`

Catálogo de tipos de persona que pueden ingresar a la empresa.

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id_tipo_persona` | INT | PK, AUTO_INCREMENT | Identificador único |
| `nombre_tipo` | VARCHAR(50) | NOT NULL, UNIQUE | Nombre del tipo |
| `descripcion` | VARCHAR(200) | NULL | Descripción del tipo |
| `estado` | ENUM | NOT NULL, DEFAULT 'activo' | 'activo' o 'inactivo' |

**Valores típicos**:
- `visitante_temporal`: Visitante temporal que ingresa por un tiempo limitado
- `empleado_propio`: Empleado propio de la empresa (planta permanente o contratista)
- `empleado_externo`: Empleado de empresa externa que trabaja temporalmente en la empresa

**Índices**:
- PRIMARY KEY: `id_tipo_persona`
- UNIQUE: `nombre_tipo`

---

### 3.2. Tabla: `persona`

Almacena toda la información de las personas (empleados y visitantes). Todos comparten los mismos atributos básicos.

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id_persona` | INT | PK, AUTO_INCREMENT | Identificador único |
| `id_tipo_persona` | INT | FK a TipoPersona, NOT NULL | Tipo de persona |
| `nombre_completo` | VARCHAR(200) | NOT NULL | Nombre completo |
| `documento` | VARCHAR(50) | NOT NULL, UNIQUE | Número de documento |
| `tipo_documento` | VARCHAR(10) | NOT NULL | 'CC', 'CE', 'NIT', etc. |
| `telefono` | VARCHAR(20) | NULL | Teléfono de contacto |
| `email` | VARCHAR(200) | NULL | Email |
| `empresa` | VARCHAR(200) | NULL | Empresa (para empleados externos o visitantes) |
| `cargo` | VARCHAR(100) | NULL | Cargo o función |
| `area` | VARCHAR(100) | NULL | Área de trabajo |
| `estado` | ENUM | NOT NULL, DEFAULT 'activo' | 'activo' o 'inactivo' |
| `fecha_registro` | DATETIME | NOT NULL, DEFAULT NOW() | Fecha de registro |
| `fecha_actualizacion` | DATETIME | NULL | Última actualización |
| `creado_por` | INT | FK a UsuarioSistema, NULL | Usuario que creó el registro |

**Índices**:
- PRIMARY KEY: `id_persona`
- UNIQUE: `documento`
- INDEX: `id_tipo_persona`, `estado`, `documento`
- FOREIGN KEY: `id_tipo_persona` REFERENCES `tipo_persona(id_tipo_persona)`
- FOREIGN KEY: `creado_por` REFERENCES `usuario_sistema(id_usuario)`

**Notas**:
- Una sola tabla para todos los tipos de persona
- Los campos `empresa`, `cargo`, `area` se usan según el tipo de persona
- `estado` controla si la persona puede acceder
- **IMPORTANTE**: Todas las personas deben tener un embedding facial activo en la tabla `reconocimiento_facial` para poder ingresar

---

### 3.3. Tabla: `reconocimiento_facial`

Almacena los embeddings faciales (vectores de características) generados por el modelo de reconocimiento facial (MVP: face_recognition, DeepFace o MediaPipe; futuras iteraciones pueden usar ArcFace).

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id_reconocimiento` | INT | PK, AUTO_INCREMENT | Identificador único |
| `id_persona` | INT | FK a Persona, NOT NULL | Persona asociada |
| `embedding` | BLOB | NOT NULL | Vector de características faciales (dimensiones según librería; ej. 128 en face_recognition) |
| `foto_referencia` | VARCHAR(500) | NULL | Ruta/URL de la foto de referencia |
| `calidad_embedding` | FLOAT | NULL | Score de calidad del embedding (0-1) |
| `modelo_version` | VARCHAR(50) | NOT NULL, DEFAULT 'face_recognition_v1' | Versión del modelo usado (MVP: pre-entrenado) |
| `estado` | ENUM | NOT NULL, DEFAULT 'activo' | 'activo' o 'inactivo' |
| `fecha_creacion` | DATETIME | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `fecha_actualizacion` | DATETIME | NULL | Última actualización |

**Índices**:
- PRIMARY KEY: `id_reconocimiento`
- UNIQUE: `id_persona` (una persona puede tener solo un embedding activo)
- INDEX: `estado`
- FOREIGN KEY: `id_persona` REFERENCES `persona(id_persona)`

**Notas**:
- El `embedding` es un vector de características (dimensiones según librería; en MVP face_recognition/DeepFace/MediaPipe)
- Se almacena como BLOB (puede ser JSON, binary, o formato específico según implementación)
- `calidad_embedding` indica la confiabilidad del embedding (útil para filtrar embeddings de baja calidad)
- **OBLIGATORIO**: Una persona debe tener un embedding activo para poder ingresar
- Una persona puede tener solo un embedding activo a la vez
- Para actualizar, se puede desactivar el anterior y crear uno nuevo
- El embedding se genera automáticamente durante el registro de la persona

---

### 3.4. Tabla: `autorizacion` *(fuera del MVP)*

Autorizaciones de acceso (iteraciones futuras). Para empleados se generaría automáticamente desde RRHH; para visitantes podría autorizar un empleado. En MVP todas las personas activas tienen acceso.

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id_autorizacion` | INT | PK, AUTO_INCREMENT | Identificador único |
| `id_persona` | INT | FK a Persona, NOT NULL | Persona autorizada |
| `fecha_inicio` | DATETIME | NOT NULL | Fecha/hora de inicio de autorización |
| `fecha_fin` | DATETIME | NULL | Fecha/hora de fin (NULL = permanente) |
| `estado` | ENUM | NOT NULL, DEFAULT 'activa' | 'activa', 'vencida', 'revocada' |
| `autorizado_por` | INT | FK a Persona, NULL | Empleado que autoriza (para visitantes) |
| `motivo` | TEXT | NULL | Motivo de la autorización o revocación |
| `fecha_creacion` | DATETIME | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `creado_por` | INT | FK a UsuarioSistema, NULL | Usuario del sistema que creó la autorización |

**Índices**:
- PRIMARY KEY: `id_autorizacion`
- INDEX: `id_persona`, `estado`, `fecha_inicio`, `fecha_fin`
- FOREIGN KEY: `id_persona` REFERENCES `persona(id_persona)`
- FOREIGN KEY: `autorizado_por` REFERENCES `persona(id_persona)`
- FOREIGN KEY: `creado_por` REFERENCES `usuario_sistema(id_usuario)`

**Notas**:
- **Para empleados propios/externos**: RRHH crea la autorización automáticamente (puede ser permanente con `fecha_fin = NULL`)
- **Para visitantes temporales**: Un empleado registrado puede autorizar (`autorizado_por` contiene el ID del empleado)
- `fecha_fin = NULL` significa autorización permanente (típico de empleados)
- `fecha_fin` con valor significa autorización temporal (típico de visitantes)

---

### 3.5. Tabla: `registro_acceso`

Registro de todos los ingresos y salidas por la puerta principal (auditoría).

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id_registro` | BIGINT | PK, AUTO_INCREMENT | Identificador único |
| `id_persona` | INT | FK a Persona, NOT NULL | Persona que ingresó/salió |
| `tipo_movimiento` | ENUM | NOT NULL | 'ingreso' o 'salida' |
| `metodo_identificacion` | ENUM | NOT NULL, DEFAULT 'documento' | 'documento' o 'reconocimiento_facial' |
| `fecha_hora` | DATETIME | NOT NULL, DEFAULT NOW() | Fecha y hora del movimiento |
| `resultado` | ENUM | NOT NULL | 'permitido' o 'denegado' |
| `motivo_denegacion` | VARCHAR(500) | NULL | Motivo si fue denegado |
| `similarity_score` | FLOAT | NULL | Score de similaridad (si fue reconocimiento facial) |
| `observaciones` | TEXT | NULL | Observaciones adicionales |

**Índices**:
- PRIMARY KEY: `id_registro`
- INDEX: `id_persona`, `fecha_hora`, `tipo_movimiento`, `resultado`
- FOREIGN KEY: `id_persona` REFERENCES `persona(id_persona)`

**Notas**:
- Esta tabla crece rápidamente, considerar particionamiento por fecha
- Registro inmutable (no se modifica ni elimina)
- `metodo_identificacion` indica cómo se identificó a la persona
- `similarity_score` solo tiene valor cuando `metodo_identificacion = 'reconocimiento_facial'`
- `motivo_denegacion` puede ser: "persona inactiva", "sin autorización vigente", "rostro no detectado", "persona no identificada", etc.

---

### 3.6. Tabla: `usuario_sistema`

Usuarios administrativos del sistema (RRHH, Recepción, Seguridad).

| Campo | Tipo | Restricciones | Descripción |
|-------|------|---------------|-------------|
| `id_usuario` | INT | PK, AUTO_INCREMENT | Identificador único |
| `nombre_usuario` | VARCHAR(50) | NOT NULL, UNIQUE | Nombre de usuario |
| `hash_password` | VARCHAR(255) | NOT NULL | Hash de contraseña (bcrypt) |
| `id_persona` | INT | FK a Persona, NULL | Persona asociada (empleado) |
| `rol` | ENUM | NOT NULL | 'admin', 'rrhh', 'recepcion', 'seguridad' |
| `estado` | ENUM | NOT NULL, DEFAULT 'activo' | 'activo' o 'inactivo' |
| `fecha_creacion` | DATETIME | NOT NULL, DEFAULT NOW() | Fecha de creación |
| `ultimo_acceso` | DATETIME | NULL | Último acceso al sistema |

**Índices**:
- PRIMARY KEY: `id_usuario`
- UNIQUE: `nombre_usuario`
- INDEX: `rol`, `estado`
- FOREIGN KEY: `id_persona` REFERENCES `persona(id_persona)`

**Notas**:
- `hash_password` debe usar algoritmo seguro (bcrypt, Argon2)
- `id_persona` puede ser NULL si el usuario no es empleado
- `rol` define los permisos del usuario

---

## 4. Relaciones entre Tablas

### 4.1. Diagrama de Relaciones (Texto)

```
TipoPersona (1) ──< (0..N) Persona
Persona (1) ──< (0..1) ReconocimientoFacial
Persona (1) ──< (0..N) Autorizacion
Persona (1) ──< (0..N) RegistroAcceso
Persona (1) ──< (0..1) UsuarioSistema
Persona (1) ──< (0..N) Autorizacion (autorizado_por)
UsuarioSistema (1) ──< (0..N) Persona (creado_por)
UsuarioSistema (1) ──< (0..N) Autorizacion (creado_por)
```

### 4.2. Reglas de Negocio en el Modelo

1. **Una persona tiene un solo tipo**
   - Relación N:1 con `tipo_persona`

2. **Una persona puede tener múltiples autorizaciones**
   - Pero solo una activa a la vez (validación a nivel de aplicación)

3. **Para empleados**: La autorización se genera automáticamente desde RRHH
   - `autorizado_por` puede ser NULL
   - `fecha_fin` puede ser NULL (permanente)

4. **Para visitantes**: Un empleado debe autorizar
   - `autorizado_por` debe tener un valor (ID de empleado)
   - `fecha_fin` debe tener un valor (temporal)

5. **Una persona DEBE tener un embedding facial activo para poder ingresar**
   - Relación 1:1 obligatoria con `reconocimiento_facial` (para personas activas)
   - El embedding se genera automáticamente al registrar la persona
   - Sin embedding activo, la persona no puede ser identificada y no puede ingresar

6. **Los registros de acceso son inmutables**
   - No se permiten actualizaciones ni eliminaciones

---

## 5. Flujo de Autorización Simplificado

### 5.1. Empleado Propio o Externo

1. RRHH (o administrador) registra la persona en el sistema con **foto facial (obligatoria)**
2. **Sistema genera automáticamente embedding facial** (MVP: face_recognition/DeepFace/MediaPipe):
   - Detecta rostro (modelo pre-entrenado)
   - Genera embedding y almacena en tabla `reconocimiento_facial`
3. (Fuera del MVP) RRHH crea autorización con fechas. En MVP todas las personas activas tienen acceso.
4. La persona puede ingresar usando reconocimiento facial (en MVP: si está activa; en futuro: mientras tenga autorización activa)

### 5.2. Visitante Temporal

1. Recepcionista (o administrador) registra la persona (tipo: visitante_temporal) con **foto facial (obligatoria)**
2. **Sistema genera embedding facial** (MVP: modelo pre-entrenado) y almacena en `reconocimiento_facial`
3. (Fuera del MVP) Recepcionista define autorización con fechas. En MVP el visitante activo tiene acceso.
4. El visitante puede ingresar usando reconocimiento facial (en MVP: si está activo; en futuro: en el rango de fechas autorizado)

---

## 6. Consultas Frecuentes

### 6.1. Buscar persona por reconocimiento facial (Método Principal)

```sql
-- Nota: Esta consulta obtiene todos los embeddings activos para comparación.
-- La comparación de embeddings (similaridad coseno) se hace en el servicio de IA.
SELECT p.*, rf.embedding, rf.calidad_embedding, rf.id_reconocimiento
FROM persona p
JOIN reconocimiento_facial rf ON p.id_persona = rf.id_persona
WHERE rf.estado = 'activo'
  AND p.estado = 'activo';
```

### 6.1.1. Validar si una persona identificada puede ingresar

```sql
-- Después de identificar a la persona por reconocimiento facial
SELECT p.*, a.id_autorizacion
FROM persona p
LEFT JOIN autorizacion a ON p.id_persona = a.id_persona 
  AND a.estado = 'activa'
  AND (a.fecha_fin IS NULL OR a.fecha_fin >= NOW())
  AND a.fecha_inicio <= NOW()
WHERE p.id_persona = ?
  AND p.estado = 'activo';
```

### 6.1.2. Validar por documento (Método Alternativo)

```sql
-- Solo para casos excepcionales cuando reconocimiento facial no está disponible
SELECT p.*, a.id_autorizacion
FROM persona p
LEFT JOIN autorizacion a ON p.id_persona = a.id_persona 
  AND a.estado = 'activa'
  AND (a.fecha_fin IS NULL OR a.fecha_fin >= NOW())
  AND a.fecha_inicio <= NOW()
WHERE p.documento = ?
  AND p.estado = 'activo';
```

### 6.2. Obtener historial de accesos de una persona

```sql
SELECT ra.*, p.nombre_completo, p.documento
FROM registro_acceso ra
JOIN persona p ON ra.id_persona = p.id_persona
WHERE p.id_persona = ?
  AND ra.fecha_hora BETWEEN ? AND ?
ORDER BY ra.fecha_hora DESC;
```

### 6.3. Obtener personas actualmente dentro (con ingreso sin salida)

```sql
SELECT p.*, ra_ingreso.fecha_hora as hora_ingreso
FROM persona p
JOIN registro_acceso ra_ingreso ON p.id_persona = ra_ingreso.id_persona
LEFT JOIN registro_acceso ra_salida ON p.id_persona = ra_salida.id_persona
  AND ra_salida.tipo_movimiento = 'salida'
  AND ra_salida.fecha_hora > ra_ingreso.fecha_hora
WHERE ra_ingreso.tipo_movimiento = 'ingreso'
  AND ra_ingreso.resultado = 'permitido'
  AND ra_salida.id_registro IS NULL
ORDER BY ra_ingreso.fecha_hora DESC;
```

### 6.4. Obtener autorizaciones activas de visitantes

```sql
SELECT a.*, p.nombre_completo as persona, 
       p_autoriza.nombre_completo as autorizado_por_nombre
FROM autorizacion a
JOIN persona p ON a.id_persona = p.id_persona
LEFT JOIN persona p_autoriza ON a.autorizado_por = p_autoriza.id_persona
JOIN tipo_persona tp ON p.id_tipo_persona = tp.id_tipo_persona
WHERE a.estado = 'activa'
  AND tp.nombre_tipo = 'visitante_temporal'
  AND (a.fecha_fin IS NULL OR a.fecha_fin >= NOW());
```

---

## 7. Optimizaciones

### 7.1. Índices Adicionales

```sql
-- Consultas por fecha en registros
CREATE INDEX idx_registro_fecha_hora ON registro_acceso(fecha_hora DESC);

-- Consultas de autorizaciones activas
CREATE INDEX idx_autorizacion_activa ON autorizacion(estado, fecha_inicio, fecha_fin) 
WHERE estado = 'activa';

-- Búsqueda de personas por documento
CREATE INDEX idx_persona_documento ON persona(documento);
```

### 7.2. Particionamiento

Para la tabla `registro_acceso` (que crecerá rápidamente), considerar particionamiento por fecha:

```sql
-- Ejemplo de particionamiento mensual
PARTITION BY RANGE (YEAR(fecha_hora) * 100 + MONTH(fecha_hora))
```

---

## 8. Ventajas del Modelo Simplificado

1. **Simplicidad**: Menos tablas, más fácil de entender y mantener
2. **Flexibilidad**: Una sola tabla `persona` con todos los atributos necesarios
3. **Escalabilidad**: Fácil agregar nuevos tipos de persona sin cambiar estructura
4. **Funcionalidad**: Cubre todos los casos de uso básicos
5. **Mantenibilidad**: Menos complejidad = menos errores

---

**Documento**: Modelo de Datos Simplificado  
**Versión**: 2.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
