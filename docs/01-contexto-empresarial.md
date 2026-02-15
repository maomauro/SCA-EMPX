# 🏢 Contexto Empresarial - STI S.A.S.

> **Nota sobre alcance:** Este documento describe el contexto general de la empresa y la visión del sistema. El alcance concreto del MVP (3 semanas), tecnologías y exclusiones está definido en [08-definicion-proyecto.md](./08-definicion-proyecto.md).

## Descripción General

**Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.)** es una compañía colombiana dedicada al diseño, desarrollo e implementación de soluciones tecnológicas para sectores como banca, retail, logística y gobierno. Su enfoque está en la innovación, la seguridad de la información y la automatización de procesos críticos.

La empresa opera desde **Bogotá** y cuenta con:
- Oficinas administrativas
- Centro de desarrollo
- Pequeño data center interno
- Zonas restringidas donde solo personal autorizado puede ingresar

---

## 🧬 Identidad Corporativa

### Nombre Ficticio
**Soluciones Tecnológicas Integrales S.A.S. (STI S.A.S.)**

### Misión
Desarrollar soluciones tecnológicas confiables, seguras y escalables que impulsen la transformación digital de nuestros clientes.

### Visión
Ser líderes en Latinoamérica en innovación tecnológica, destacándonos por la calidad, seguridad y eficiencia de nuestras soluciones.

### Valores
- **Seguridad y responsabilidad**
- **Innovación continua**
- **Transparencia**
- **Excelencia técnica**
- **Confidencialidad**

---

## 🧩 Estructura Organizacional

### 1. Dirección General
Define la estrategia, alianzas y visión de la empresa.

### 2. Área de Desarrollo de Software
- Equipos de backend, frontend, QA y DevOps
- Manejan proyectos sensibles para clientes corporativos
- Acceso restringido a ciertos ambientes y repositorios

### 3. Área de Infraestructura y Seguridad
- Administración de servidores
- Gestión de redes
- Seguridad perimetral y lógica
- Acceso altamente controlado

### 4. Área de Soporte Técnico
- Atención a clientes
- Mesa de ayuda
- Soporte en sitio

### 5. Área Administrativa
- Talento humano
- Finanzas
- Compras
- Recepción

### 6. Área Comercial
- Ventas
- Relación con clientes
- Gestión de contratos

---

## 🏢 Instalaciones Físicas

La empresa cuenta con las siguientes instalaciones:

- **Recepción principal**: Punto de entrada y registro de visitantes
- **Torniquetes de acceso**: Control de ingreso automatizado
- **Oficinas abiertas**: Espacios de trabajo colaborativo
- **Salas de reuniones**: Espacios para reuniones internas y con clientes
- **Centro de desarrollo**: Zona restringida para personal técnico
- **Sala de servidores**: Acceso crítico, solo personal autorizado
- **Zona de visitantes**: Área específica para recepción de visitantes
- **Parqueadero**: Control de vehículos

**Importante**: Cada área tiene niveles de acceso distintos según la sensibilidad de la información y equipos que contiene.

---

## 👥 Tipos de Personas que Ingresan a la Empresa

### 1. Empleados
- **Planta permanente**: Personal con contrato indefinido
- **Contratistas de proyectos**: Personal temporal asignado a proyectos específicos
- **Personal de seguridad y aseo**: Personal de servicios generales

### 2. Visitantes
- **Clientes**: Representantes de empresas cliente
- **Proveedores**: Personal de empresas proveedoras
- **Consultores externos**: Profesionales independientes
- **Aspirantes a entrevistas**: Candidatos en proceso de selección

### 3. Personal Eventual
- **Técnicos de mantenimiento**: Personal especializado para mantenimiento de equipos
- **Mensajeros**: Personal de servicios de mensajería
- **Personal de soporte externo**: Técnicos de proveedores externos

---

## 🔐 Necesidad del Sistema de Control de Acceso

### Contexto de Seguridad

La empresa maneja **información sensible de clientes**, por lo que requiere:

- ✅ Control estricto de quién entra y sale
- ✅ Registro de visitantes con trazabilidad completa
- ✅ Validación de autorizaciones en tiempo real
- ✅ Integración con torniquetes y puertas automáticas
- ✅ Auditoría completa para incidentes de seguridad

### Incidentes Históricos

La empresa ha tenido incidentes menores que justifican la implementación del sistema:

- ❌ **Visitantes ingresando sin autorización formal**: Falta de control en el registro de visitantes
- ❌ **Empleados olvidando registrar salida**: Ausencia de registro automático
- ❌ **Falta de control de accesos**: No se sabe quién ingresa y sale
- ❌ **Falta de trazabilidad en auditorías internas**: Imposibilidad de rastrear accesos históricos

### Justificación

Estos incidentes, aunque menores, representan un riesgo para:
- La seguridad de la información de clientes
- El cumplimiento de políticas de seguridad
- La confidencialidad de proyectos en desarrollo
- La integridad de la infraestructura crítica

---

## 🧠 Cómo Encaja la Solución en este Contexto

El **Sistema de Control de Acceso Físico (SCA-EMPX)** permitirá:

### ✅ Registro Previo de Empleados y Visitantes
- Datos básicos de identificación
- **Reconocimiento facial obligatorio** (en MVP: librerías pre-entrenadas como face_recognition, DeepFace o MediaPipe; ver 08-definicion-proyecto.md)
- Generación automática de embeddings faciales
- Gestión de autorizaciones por persona (iteraciones futuras; en MVP todas las personas activas tienen acceso)

### ✅ Validación Automática por Reconocimiento Facial
- **Método principal**: Reconocimiento facial (en MVP: librerías pre-entrenadas)
- Solo ingresan personas activas (y autorizadas en iteraciones futuras)
- Validación en tiempo real (< 10 segundos para MVP)
- Identificación automática sin necesidad de documento
- Respuesta vía API (integración con dispositivos físicos en iteraciones futuras)

### ✅ Registro de Entrada y Salida
- Trazabilidad completa de todos los movimientos
- Registro automático sin intervención manual
- Historial completo para auditorías

### ✅ Control de Acceso General
- Solo personas activas pueden ingresar (MVP); en futuras iteraciones: autorizaciones por persona
- Configuración flexible de autorizaciones (fuera del MVP)
- Restricciones temporales por fecha (fuera del MVP)

### ✅ Panel de Administración
- Interfaz para RRHH, seguridad y recepción
- Gestión centralizada de personas y autorizaciones
- Configuración de reglas y políticas

### ✅ Auditoría Completa
- Historial completo para revisiones internas
- Soporte para investigaciones de incidentes
- Reportes personalizables por fecha y persona

---

## 📊 Impacto Esperado

Con la implementación del sistema se espera:

- 🔒 **Mejora en seguridad física**: Reducción de accesos no autorizados
- 📋 **Cumplimiento normativo**: Soporte para auditorías y certificaciones
- ⚡ **Eficiencia operativa**: Automatización de procesos manuales
- 📈 **Visibilidad**: Información para toma de decisiones estratégicas

---

**Documento**: Contexto Empresarial  
**Versión**: 1.0  
**Fecha**: 2026
