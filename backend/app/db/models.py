"""
Modelos ORM — SQLite.

Esquema:
  areas → cargos → personas → tipos_persona
  personas → registros  (embeddings faciales + eventos)
  personas → visitas     (historial de visitas con motivo)
"""
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean, Column, DateTime, Float, ForeignKey,
    Integer, LargeBinary, String, Text,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


# ── Catálogos ────────────────────────────────────────────────────────────────

class Area(Base):
    """Catálogo de áreas organizacionales de la empresa.

    Representa las divisiones o departamentos internos (p. ej. Recursos Humanos,
    TI, Producción). Es el nivel más alto de la jerarquía organizacional dentro
    del sistema; cada cargo pertenece a exactamente un área.

    Attributes:
        id_area: Llave primaria autoincremental.
        nombre:  Nombre único del área (máx. 100 caracteres).
        cargos:  Cargos asociados a esta área.
    """
    __tablename__ = "areas"

    id_area    = Column(Integer, primary_key=True, autoincrement=True)
    nombre     = Column(String(100), unique=True, nullable=False)

    cargos     = relationship("Cargo", back_populates="area")


class Cargo(Base):
    """Catálogo de cargos o puestos de trabajo dentro de un área.

    Un cargo agrupa a los empleados que desempeñan el mismo rol (p. ej.
    Analista de Datos, Supervisor de Planta). Solo aplica a personas cuyo
    ``TipoPersona.es_empleado`` sea ``True``; visitantes y contratistas
    dejan ``id_cargo`` en ``NULL``.

    Attributes:
        id_cargo: Llave primaria autoincremental.
        nombre:   Nombre del cargo (máx. 100 caracteres).
        id_area:  FK al área a la que pertenece este cargo.
        area:     Relación hacia el área padre.
        personas: Empleados que ocupan este cargo.
    """
    __tablename__ = "cargos"

    id_cargo   = Column(Integer, primary_key=True, autoincrement=True)
    nombre     = Column(String(100), nullable=False)
    id_area    = Column(Integer, ForeignKey("areas.id_area"), nullable=False)

    area       = relationship("Area", back_populates="cargos")
    personas   = relationship("Persona", back_populates="cargo")


class TipoPersona(Base):
    """Catálogo de clasificaciones de personas que interactúan con el sistema.

    Define si una persona es empleado interno, visitante externo o contratista.
    El flag ``es_empleado`` determina si se le exige un cargo asignado y si sus
    accesos se registran como eventos laborales.

    Valores semilla esperados:
        - ``Empleado``   (``es_empleado=True``)
        - ``Visitante``  (``es_empleado=False``)
        - ``Contratista``(``es_empleado=False``)

    Attributes:
        id_tipo_persona: Llave primaria autoincremental.
        tipo:            Nombre único del tipo (máx. 50 caracteres).
        descripcion:     Descripción opcional del tipo.
        es_empleado:     ``True`` si el tipo corresponde a personal interno.
        personas:        Personas clasificadas con este tipo.
    """
    __tablename__ = "tipos_persona"

    id_tipo_persona = Column(Integer, primary_key=True, autoincrement=True)
    tipo            = Column(String(50), unique=True, nullable=False)   # Empleado | Visitante | Contratista
    descripcion     = Column(String(200), nullable=True)
    es_empleado     = Column(Boolean, nullable=False, default=False)

    personas        = relationship("Persona", back_populates="tipo_persona")


# ── Entidades principales ─────────────────────────────────────────────────────

class Persona(Base):
    """Entidad central que representa a cualquier individuo registrado en el sistema.

    Almacena la identidad documental y organizacional de empleados, visitantes
    y contratistas. El reconocimiento facial se resuelve a través de los
    embeddings almacenados en ``Registro``. Un mismo individuo puede tener
    múltiples registros faciales para mejorar la precisión del modelo.

    Attributes:
        id_persona:      Llave primaria autoincremental.
        tipo_documento:  Tipo de documento de identidad
                         (``CC`` | ``CE`` | ``PAS`` | ``NIT``).
        nro_documento:   Número de documento único por persona.
        nombres:         Nombre completo (máx. 200 caracteres).
        id_tipo_persona: FK al tipo de persona (empleado, visitante, etc.).
        id_cargo:        FK al cargo; ``NULL`` para no-empleados.
        fecha_registro:  Timestamp UTC de creación del registro.
        activo:          ``False`` bloquea el acceso sin eliminar el historial.
        tipo_persona:    Relación hacia el tipo de persona.
        cargo:           Relación hacia el cargo asignado.
        registros:       Embeddings y eventos de acceso asociados.
        visitas:         Historial de visitas (solo no-empleados).
    """
    __tablename__ = "personas"

    id_persona      = Column(Integer, primary_key=True, autoincrement=True)
    tipo_documento  = Column(String(10), nullable=False, default="CC")   # CC | CE | PAS | NIT
    nro_documento   = Column(String(50), unique=True, nullable=False)
    nombres         = Column(String(200), nullable=False)
    id_tipo_persona = Column(Integer, ForeignKey("tipos_persona.id_tipo_persona"), nullable=False)
    # Solo aplica si es_empleado=True en su tipo; null para visitantes/contratistas sin cargo
    id_cargo        = Column(Integer, ForeignKey("cargos.id_cargo"), nullable=True)
    fecha_registro  = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    activo          = Column(Boolean, nullable=False, default=True)

    tipo_persona    = relationship("TipoPersona", back_populates="personas")
    cargo           = relationship("Cargo", back_populates="personas")
    registros       = relationship("Registro", back_populates="persona", cascade="all, delete-orphan")
    visitas         = relationship("Visita", back_populates="persona", cascade="all, delete-orphan")


class Registro(Base):
    """Embedding facial y log de eventos de acceso de una persona.

    Cada fila corresponde a un frame procesado por el modelo de reconocimiento
    facial. Tiene dos roles según el campo ``evento``:

    - ``'registro'``: capturado durante el alta de la persona; forma la galería
      de referencia usada para identificación posterior.
    - ``'acceso'``: capturado al momento de una entrada o salida; incluye el
      score de similitud coseno contra la galería.

    El embedding se serializa como un arreglo de 512 valores ``float32``
    en orden *little-endian* (2048 bytes totales).

    Attributes:
        id_registro:      Llave primaria autoincremental.
        id_persona:       FK a la persona identificada.
        evento:           Tipo de evento: ``'registro'`` o ``'acceso'``.
        tipo_acceso:      Dirección del acceso: ``'entrada'``, ``'salida'``
                          o ``NULL`` cuando ``evento='registro'``.
        embedding_facial: Vector 512-d serializado (512 × float32 = 2048 bytes).
        similitud:        Score coseno del match; ``NULL`` en eventos de alta.
        fecha:            Timestamp UTC del evento.
        persona:          Relación hacia la persona propietaria del registro.
    """
    __tablename__ = "registros"

    id_registro      = Column(Integer, primary_key=True, autoincrement=True)
    id_persona       = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    evento           = Column(String(20), nullable=False)        # registro | acceso
    tipo_acceso      = Column(String(10), nullable=True)         # entrada | salida | null
    embedding_facial = Column(LargeBinary, nullable=False)       # 512 x float32 = 2048 bytes
    similitud        = Column(Float, nullable=True)              # score coseno (solo en acceso)
    fecha            = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    persona          = relationship("Persona", back_populates="registros")


class Visita(Base):
    """Historial de visitas de personas no-empleadas (visitantes y contratistas).

    Registra cada ingreso a las instalaciones indicando el motivo de la visita
    y el rango horario. Si la persona ya tiene embeddings en la galería, el
    sistema la identifica automáticamente y solo solicita el motivo; de lo
    contrario se captura su información documental en el flujo de registro.

    ``fecha_salida`` se rellena cuando la persona abandona las instalaciones;
    mientras sea ``NULL`` la visita se considera activa.

    Attributes:
        id_visita:    Llave primaria autoincremental.
        id_persona:   FK a la persona que realiza la visita.
        motivo:       Descripción del propósito de la visita (texto libre).
        fecha:        Timestamp UTC de ingreso.
        fecha_salida: Timestamp UTC de salida; ``NULL`` si la visita sigue activa.
        persona:      Relación hacia la persona visitante.
    """
    __tablename__ = "visitas"

    id_visita    = Column(Integer, primary_key=True, autoincrement=True)
    id_persona   = Column(Integer, ForeignKey("personas.id_persona"), nullable=False)
    motivo       = Column(Text, nullable=False)
    fecha        = Column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    fecha_salida = Column(DateTime, nullable=True)

    persona     = relationship("Persona", back_populates="visitas")
