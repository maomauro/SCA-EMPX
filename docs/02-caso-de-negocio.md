# 💼 Caso de Negocio - Sistema de Control de Acceso

## Resumen Ejecutivo

Este documento presenta la justificación de negocio para la implementación del **Sistema de Control de Acceso Físico y Registro de Ingresos/Salidas (SCA-EMPX)** en Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.).

El sistema permitirá gestionar de forma automatizada y segura el acceso físico a las instalaciones de la empresa, garantizando trazabilidad completa y cumplimiento de políticas de seguridad.

---

## 🔴 Problema Actual

### Situación Actual

La empresa actualmente enfrenta las siguientes limitaciones en el control de acceso:

#### 1. Falta de Control Centralizado
- No existe un sistema centralizado que gestione quién entra y sale de las instalaciones
- Los registros se realizan de forma manual (papel, Excel) o no se realizan
- No hay integración entre diferentes puntos de acceso

#### 2. Gestión Manual de Visitantes
- Visitantes pueden ingresar sin registro formal o con registros manuales poco confiables
- Dificultad para validar autorizaciones en tiempo real
- Falta de trazabilidad de visitas históricas

#### 3. Ausencia de Trazabilidad Confiable
- No hay registro confiable para auditorías de seguridad
- Imposibilidad de responder rápidamente a preguntas como:
  - "¿Quién estuvo en la empresa el día X a las Y horas?"
  - "¿Qué visitantes ingresaron la semana pasada?"
  - "¿Quién está actualmente dentro de la empresa?"

#### 4. Falta de Control de Accesos
- No hay control de quién ingresa y sale de la empresa
- Dificultad para restringir accesos temporales

#### 5. Dificultad para Responder a Incidentes
- Ante un incidente de seguridad, no hay evidencia confiable de accesos
- Investigaciones requieren tiempo excesivo
- Falta de datos para análisis forense

### Incidentes Reportados

La empresa ha registrado los siguientes incidentes menores:

- ❌ Visitantes ingresando sin autorización formal
- ❌ Empleados olvidando registrar salida
- ❌ Falta de control de accesos
- ❌ Falta de trazabilidad en auditorías internas

Aunque estos incidentes son menores, representan un riesgo creciente para la seguridad de la información.

---

## 🎯 Objetivo de la Solución

Implementar un sistema de control de acceso que:

### Objetivos Principales

1. **Garantizar que solo personas autorizadas ingresen**
   - **Validación automática por reconocimiento facial** (método principal)
   - Identificación mediante reconocimiento facial (en MVP: librerías pre-entrenadas como face_recognition, DeepFace o MediaPipe; ver [08-definicion-proyecto.md](./08-definicion-proyecto.md))
   - Verificación de estado (activo/inactivo)
   - Validación de autorizaciones vigentes (en iteraciones futuras; en MVP todas las personas activas tienen acceso)

2. **Registrar de forma automática y confiable entradas y salidas**
   - Registro automático sin intervención manual
   - Trazabilidad completa de todos los eventos
   - Historial permanente para auditorías

3. **Permitir gestión de autorizaciones por persona** (iteraciones futuras; en MVP no se implementa)
   - Configuración flexible de permisos
   - Restricciones temporales y por horario
   - Control de acceso general de la empresa

4. **Proveer trazabilidad completa para auditorías internas y externas**
   - Historial completo de accesos
   - Reportes personalizables
   - Soporte para investigaciones

---

## ✅ Beneficios Esperados

### 1. Seguridad Física y Lógica Mejorada

#### Reducción de Riesgo de Intrusiones
- Control estricto de acceso reduce la probabilidad de intrusiones no autorizadas
- Validación en tiempo real por reconocimiento facial previene accesos no autorizados
- Registro automático permite detección temprana de patrones sospechosos

#### Protección de Áreas Críticas
- Control de acceso general de la empresa
- Solo personas autorizadas pueden ingresar
- Restricciones temporales para acceso puntual

**Impacto Cuantificable**:
- Reducción estimada del 80% en accesos no autorizados
- Control del 100% de los accesos a la empresa

### 2. Cumplimiento Normativo y Contractual

#### Soporte a Estándares de Seguridad
- Soporte a políticas de seguridad de la información (ISO 27001, NIST, etc.)
- Evidencia para auditorías de clientes y entes reguladores
- Cumplimiento de acuerdos de confidencialidad (NDA)

#### Trazabilidad para Auditorías
- Historial completo de accesos disponible para auditorías
- Reportes exportables en formatos estándar
- Soporte para investigaciones de seguridad

**Impacto Cuantificable**:
- 100% de trazabilidad de accesos para auditorías
- Reducción del 60% en tiempo de preparación para auditorías

### 3. Eficiencia Operativa

#### Eliminación de Procesos Manuales
- Eliminación de registros manuales en recepción
- Automatización del control de visitantes
- Reducción de errores humanos

#### Integración con Procesos de RRHH
- Integración con procesos de altas/bajas de empleados
- Sincronización automática de estados (activo/inactivo)
- Reducción de tiempo administrativo

**Impacto Cuantificable**:
- Reducción del 70% en tiempo de registro de visitantes
- Ahorro de 10 horas/semana en tareas administrativas de RRHH

### 4. Información para Toma de Decisiones

#### Reportes y Análisis
- Reportes de ocupación y horarios pico
- Análisis de patrones de acceso
- Métricas de uso de instalaciones

#### Soporte Estratégico
- Información para decisiones de seguridad
- Optimización de recursos de seguridad
- Planificación de capacidad

**Impacto Cuantificable**:
- Disponibilidad de métricas en tiempo real
- Reducción del 40% en tiempo de análisis de incidentes

---

## ⚠️ Riesgos de No Implementar

### Riesgos Operacionales

1. **Continuidad de Accesos No Controlados**
   - Persistencia de vulnerabilidades de seguridad
   - Incremento en probabilidad de incidentes mayores

2. **Dificultad para Investigar Incidentes**
   - Falta de evidencia para investigaciones
   - Tiempo excesivo en análisis forense
   - Imposibilidad de identificar responsables

3. **Pérdida de Confianza de Clientes**
   - Clientes que exigen altos estándares de seguridad pueden perder confianza
   - Impacto negativo en relaciones comerciales
   - Posible pérdida de contratos

4. **Incumplimientos Normativos**
   - Incumplimiento de políticas internas de seguridad
   - Violación de acuerdos de confidencialidad (NDA)
   - Riesgo de sanciones o multas

### Impacto Financiero Potencial

- **Pérdida de contratos**: Clientes corporativos pueden exigir sistemas de control de acceso
- **Multas y sanciones**: Por incumplimiento de políticas de seguridad
- **Costos de incidentes**: Investigaciones, remediación, pérdida de reputación
- **Costos de auditorías**: Tiempo y recursos para preparar auditorías sin sistema

---

## 💰 Análisis de Inversión

### Costos Estimados

#### Desarrollo e Implementación
- Desarrollo del sistema
- Integración con dispositivos físicos
- Capacitación de usuarios
- Migración de datos (si aplica)

#### Infraestructura (si aplica)
- Servidores y almacenamiento
- Licencias de software
- Dispositivos adicionales (si se requieren)

#### Operación y Mantenimiento
- Mantenimiento del sistema
- Soporte técnico
- Actualizaciones y mejoras

### Retorno de la Inversión (ROI)

#### Beneficios Cuantificables
- Ahorro en tiempo administrativo: **10 horas/semana**
- Reducción en tiempo de auditorías: **60% menos tiempo**
- Reducción en incidentes de seguridad: **80% menos accesos no autorizados**

#### Beneficios Cualitativos
- Mejora en seguridad y confianza
- Cumplimiento normativo
- Protección de información sensible
- Mejora en imagen corporativa

### Período de Recuperación

El período de recuperación de la inversión se estima en **12-18 meses** considerando:
- Ahorro en tiempo administrativo
- Reducción en costos de auditorías
- Prevención de incidentes de seguridad

---

## 📊 Métricas de Éxito

### Indicadores Clave de Rendimiento (KPI)

1. **Tasa de Accesos No Autorizados**
   - Meta: Reducción del 80% en el primer año

2. **Tiempo de Registro de Visitantes**
   - Meta: Reducción del 70% en tiempo de registro

3. **Trazabilidad de Accesos**
   - Meta: 100% de accesos registrados

4. **Tiempo de Respuesta a Auditorías**
   - Meta: Reducción del 60% en tiempo de preparación

5. **Satisfacción de Usuarios**
   - Meta: 85% de satisfacción en encuestas

---

## ✅ Recomendación

Se recomienda **proceder con la implementación** del Sistema de Control de Acceso Físico (SCA-EMPX) debido a:

1. **Necesidad crítica**: Los incidentes reportados y la falta de control actual representan un riesgo significativo
2. **Beneficios claros**: Mejora en seguridad, eficiencia y cumplimiento normativo
3. **ROI positivo**: Retorno de inversión estimado en 12-18 meses
4. **Riesgo de no implementar**: Costos potenciales superan los costos de implementación

---

**Documento**: Caso de Negocio  
**Versión**: 1.0  
**Fecha**: 2026  
**Autor**: Equipo de Proyecto STI S.A.S.
