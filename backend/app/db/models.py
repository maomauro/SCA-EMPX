"""
Modelos ORM para SQLite. Referencia: docs/05-modelo-datos.md.
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, ForeignKey,
    Enum as SQLEnum, LargeBinary,
)
from sqlalchemy.orm import relationship

from backend.app.db.database import Base

import enum


class EstadoPersona(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"


class EstadoReconocimiento(str, enum.Enum):
    activo = "activo"
    inactivo = "inactivo"


class TipoMovimiento(str, enum.Enum):
    ingreso = "ingreso"
    salida = "salida"


class ResultadoAcceso(str, enum.Enum):
    permitido = "permitido"
    denegado = "denegado"


class MetodoIdentificacion(str, enum.Enum):
    documento = "documento"
    reconocimiento_facial = "reconocimiento_facial"


class RolUsuario(str, enum.Enum):
    admin = "admin"
    rrhh = "rrhh"
    recepcion = "recepcion"
    seguridad = "seguridad"


# --- Catálogos ---

class TipoPersona(Base):
    __tablename__ = "tipo_persona"

    id_tipo_persona = Column(Integer, primary_key=True, autoincrement=True)
    nombre_tipo = Column(String(50), unique=True, nullable=False)
    descripcion = Column(String(200), nullable=True)
    estado = Column(String(20), nullable=False, default="activo")


# --- Entidades principales ---

class Persona(Base):
    __tablename__ = "persona"

    id_persona = Column(Integer, primary_key=True, autoincrement=True)
    id_tipo_persona = Column(Integer, ForeignKey("tipo_persona.id_tipo_persona"), nullable=False)
    nombre_completo = Column(String(200), nullable=False)
    documento = Column(String(50), unique=True, nullable=False)
    tipo_documento = Column(String(10), nullable=False, default="CC")
    telefono = Column(String(20), nullable=True)
    email = Column(String(200), nullable=True)
    empresa = Column(String(200), nullable=True)
    motivo_visita = Column(String(500), nullable=True)  # HU-03 visitante
    id_empleado_visitado = Column(Integer, ForeignKey("persona.id_persona"), nullable=True)  # HU-03 opcional
    cargo = Column(String(100), nullable=True)
    area = Column(String(100), nullable=True)
    estado = Column(String(20), nullable=False, default="activo")
    fecha_registro = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=True, onupdate=datetime.utcnow)
    creado_por = Column(Integer, nullable=True)  # FK a usuario_sistema.id_usuario (evita ciclo en create_all)

    tipo_persona = relationship("TipoPersona", backref="personas")
    empleado_visitado = relationship("Persona", remote_side=[id_persona], foreign_keys=[id_empleado_visitado])
    reconocimiento_facial = relationship("ReconocimientoFacial", back_populates="persona", uselist=False)
    registros_acceso = relationship("RegistroAcceso", back_populates="persona")


class ReconocimientoFacial(Base):
    __tablename__ = "reconocimiento_facial"

    id_reconocimiento = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey("persona.id_persona"), nullable=False)
    embedding = Column(LargeBinary, nullable=False)  # BLOB: vector serializado
    foto_referencia = Column(String(500), nullable=True)
    calidad_embedding = Column(Float, nullable=True)
    modelo_version = Column(String(50), nullable=False, default="face_recognition_v1")
    estado = Column(String(20), nullable=False, default="activo")
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = Column(DateTime, nullable=True, onupdate=datetime.utcnow)

    persona = relationship("Persona", back_populates="reconocimiento_facial")


class RegistroAcceso(Base):
    __tablename__ = "registro_acceso"

    id_registro = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey("persona.id_persona"), nullable=False)
    tipo_movimiento = Column(String(20), nullable=False)  # ingreso | salida
    metodo_identificacion = Column(String(30), nullable=False, default="reconocimiento_facial")
    fecha_hora = Column(DateTime, nullable=False, default=datetime.utcnow)
    resultado = Column(String(20), nullable=False)  # permitido | denegado
    motivo_denegacion = Column(String(500), nullable=True)
    similarity_score = Column(Float, nullable=True)
    observaciones = Column(Text, nullable=True)

    persona = relationship("Persona", back_populates="registros_acceso")


class Autorizacion(Base):
    """Autorización de visita para un visitante. HU-04."""
    __tablename__ = "autorizacion"

    id_autorizacion = Column(Integer, primary_key=True, autoincrement=True)
    id_persona = Column(Integer, ForeignKey("persona.id_persona"), nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_fin = Column(DateTime, nullable=False)
    estado = Column(String(20), nullable=False, default="vigente")  # vigente | vencida | cancelada
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)

    persona = relationship("Persona", backref="autorizaciones")


class UsuarioSistema(Base):
    __tablename__ = "usuario_sistema"

    id_usuario = Column(Integer, primary_key=True, autoincrement=True)
    nombre_usuario = Column(String(50), unique=True, nullable=False)
    hash_password = Column(String(255), nullable=False)
    id_persona = Column(Integer, ForeignKey("persona.id_persona"), nullable=True)
    rol = Column(String(20), nullable=False)  # admin, rrhh, recepcion, seguridad
    estado = Column(String(20), nullable=False, default="activo")
    fecha_creacion = Column(DateTime, nullable=False, default=datetime.utcnow)
    ultimo_acceso = Column(DateTime, nullable=True)

    persona = relationship("Persona", backref="usuario_sistema", foreign_keys="UsuarioSistema.id_persona")
