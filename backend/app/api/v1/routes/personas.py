"""
Endpoints de gestión de personas.

Permite crear personas, listarlas, obtener detalle, identificarlas por cara
y añadir embeddings faciales de registro.

Rutas:
    POST /personas/                  → Crea una persona sin fotos.
    GET  /personas/                  → Lista personas activas (filtro opcional por tipo).
    GET  /personas/{id}              → Detalle de una persona.
    POST /personas/identificar       → Identifica persona por imagen (visitante recurrente).
    GET  /personas/buscar-por-cara   → Placeholder informativo.
    POST /personas/{id}/registros    → Añade un embedding de registro a la galería.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.app.db.database import get_db
from backend.app.db.models import Persona, Registro, TipoPersona
from backend.app.ml.face_model import (
    get_embedding_from_bytes, embedding_to_bytes, bytes_to_embedding,
    find_best_match,
)
from backend.app.config.config import FACE_SIMILARITY_THRESHOLD, MAX_EMBEDDINGS_PER_PERSONA

router = APIRouter()


# ── Schemas inline ────────────────────────────────────────────────────────────

class PersonaCreate(BaseModel):
    """Schema de entrada para crear una persona.

    Attributes:
        tipo_documento:  Tipo de documento (``CC`` | ``CE`` | ``PAS`` | ``NIT``).
        nro_documento:   Número de documento único.
        nombres:         Nombre completo.
        id_tipo_persona: FK al catálogo ``tipos_persona``.
        id_cargo:        FK al catálogo ``cargos``; requerido si es empleado.
    """
    tipo_documento:  str
    nro_documento:   str
    nombres:         str
    id_tipo_persona: int
    id_cargo:        Optional[int] = None


class PersonaUpdate(BaseModel):
    """Schema de entrada para actualizar una persona.

    Attributes:
        activo: Estado activo/inactivo.
        estado: Estado como string ("activo" o "inactivo").
    """
    activo: Optional[bool] = None
    estado: Optional[str] = None


class PersonaOut(BaseModel):
    """Schema de salida con datos completos de una persona.

    Attributes:
        id_persona:      Identificador único.
        tipo_documento:  Tipo de documento.
        nro_documento:   Número de documento.
        nombres:         Nombre completo.
        id_tipo_persona: FK al tipo de persona.
        tipo:            Nombre del tipo (Empleado / Visitante / Contratista).
        id_cargo:        FK al cargo; ``None`` para no-empleados.
        cargo:           Nombre del cargo o ``None``.
        area:            Nombre del área o ``None``.
        n_embeddings:    Cantidad de embeddings de registro almacenados.
        activo:          ``False`` si la persona está bloqueada.
    """
    id_persona:      int
    tipo_documento:  str
    nro_documento:   str
    nombres:         str
    id_tipo_persona: int
    tipo:            str
    id_cargo:        Optional[int]
    cargo:           Optional[str]
    area:            Optional[str]
    n_embeddings:    int
    activo:          bool

    class Config:
        from_attributes = True


def _persona_out(p: Persona) -> dict:
    """Serializa un objeto ``Persona`` ORM a diccionario de respuesta.

    Args:
        p: Instancia ORM de ``Persona`` con relaciones cargadas.

    Returns:
        Diccionario con todos los campos de ``PersonaOut`` más ``es_empleado``.
    """
    n = len([r for r in p.registros if r.evento == "registro"])
    return {
        "id_persona":      p.id_persona,
        "tipo_documento":  p.tipo_documento,
        "nro_documento":   p.nro_documento,
        "nombres":         p.nombres,
        "id_tipo_persona": p.id_tipo_persona,
        "tipo":            p.tipo_persona.tipo if p.tipo_persona else "",
        "es_empleado":     p.tipo_persona.es_empleado if p.tipo_persona else False,
        "id_cargo":        p.id_cargo,
        "cargo":           p.cargo.nombre if p.cargo else None,
        "area":            p.cargo.area.nombre if p.cargo and p.cargo.area else None,
        "n_embeddings":    n,
        "activo":          p.activo,
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/")
def crear_persona(body: PersonaCreate, db: Session = Depends(get_db)):
    """Registra una nueva persona en el sistema sin capturas faciales.

    Los embeddings se agregan en pasos posteriores vía
    ``POST /personas/{id}/registros``.

    Args:
        body: Datos de la persona a registrar.
        db:   Sesión de base de datos.

    Returns:
        Diccionario con los datos de la persona creada.

    Raises:
        HTTPException: 409 si el documento ya existe.
        HTTPException: 400 si el tipo de persona no existe.
        HTTPException: 400 si es empleado y no tiene cargo.
    """
    if db.query(Persona).filter(Persona.nro_documento == body.nro_documento).first():
        raise HTTPException(409, "Ya existe una persona con ese documento.")
    tipo = db.query(TipoPersona).filter(TipoPersona.id_tipo_persona == body.id_tipo_persona).first()
    if not tipo:
        raise HTTPException(400, "Tipo de persona no válido.")
    if tipo.es_empleado and not body.id_cargo:
        raise HTTPException(400, "Los empleados deben tener un cargo asignado.")

    p = Persona(
        tipo_documento=body.tipo_documento,
        nro_documento=body.nro_documento,
        nombres=body.nombres.strip(),
        id_tipo_persona=body.id_tipo_persona,
        id_cargo=body.id_cargo,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _persona_out(p)


@router.post("/registro-completo")
async def crear_persona_con_foto(
    nombre_completo: str = Form(...),
    documento: str = Form(...),
    tipo_documento: str = Form("CC"),
    cargo: str = Form(None),
    area: str = Form(None),
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Registra una nueva persona con foto en un solo paso.
    
    Este endpoint maneja el formulario multipart/form-data del frontend
    y crea la persona junto con su primer embedding facial.
    
    Args:
        nombre_completo: Nombre completo de la persona.
        documento: Número de documento.
        tipo_documento: Tipo de documento (CC, CE, PAS, NIT).
        cargo: Cargo (opcional, para empleados).
        area: Área (opcional, para empleados).
        foto: Archivo de imagen con el rostro.
        db: Sesión de base de datos.
        
    Returns:
        Diccionario con los datos de la persona creada.
        
    Raises:
        HTTPException: 409 si el documento ya existe.
        HTTPException: 400 si no se detecta rostro en la foto.
    """
    # Verificar si ya existe
    if db.query(Persona).filter(Persona.nro_documento == documento).first():
        raise HTTPException(409, "Ya existe una persona con ese documento.")
    
    # Determinar tipo de persona (Empleado por defecto si tiene cargo)
    tipo_persona = db.query(TipoPersona).filter(
        TipoPersona.tipo == ("Empleado" if cargo else "Visitante")
    ).first()
    if not tipo_persona:
        raise HTTPException(400, "Tipo de persona no encontrado.")
    
    # Buscar cargo si se especificó
    id_cargo = None
    if cargo:
        from backend.app.db.models import Cargo
        cargo_obj = db.query(Cargo).filter(Cargo.nombre == cargo).first()
        if cargo_obj:
            id_cargo = cargo_obj.id_cargo
    
    # Crear persona
    p = Persona(
        tipo_documento=tipo_documento,
        nro_documento=documento,
        nombres=nombre_completo.strip(),
        id_tipo_persona=tipo_persona.id_tipo_persona,
        id_cargo=id_cargo,
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    
    # Procesar foto y crear embedding
    img_bytes = await foto.read()
    emb = get_embedding_from_bytes(img_bytes)
    if emb is None:
        # Si no se detecta rostro, eliminar la persona creada
        db.delete(p)
        db.commit()
        raise HTTPException(400, "No se detectó un rostro en la foto proporcionada.")
    
    # Guardar embedding
    reg = Registro(
        id_persona=p.id_persona,
        evento="registro",
        tipo_acceso=None,
        embedding_facial=embedding_to_bytes(emb),
        similitud=None,
    )
    db.add(reg)
    db.commit()
    
    return _persona_out(p)


@router.get("/")
def listar_personas(
    tipo: Optional[str] = None,
    estado: Optional[str] = None,
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Retorna la lista de personas, opcionalmente filtrada.

    Args:
        tipo: Nombre del tipo de persona (``'empleado'``, ``'visitante'``, ``'contratista'``).
        estado: Filtro de estado (``'activos'``, ``'inactivos'``, ``'todos'``). Por defecto 'activos'.
        q: Búsqueda por nombre o documento.
        db: Sesión de base de datos.

    Returns:
        Lista de diccionarios ordenada alfabéticamente por ``nombres``.
    """
    q_obj = db.query(Persona)
    
    # Filtrar por estado
    if estado == "todos":
        pass  # No filtrar por activo
    elif estado == "inactivos":
        q_obj = q_obj.filter(Persona.activo.is_(False))
    else:  # Por defecto activos
        q_obj = q_obj.filter(Persona.activo.is_(True))
    
    # Filtrar por tipo
    if tipo:
        tipo_lower = tipo.lower()
        q_obj = q_obj.join(TipoPersona).filter(
            TipoPersona.tipo.ilike(f"%{tipo_lower}%")
        )
    
    # Búsqueda por texto
    if q:
        q_obj = q_obj.filter(
            (Persona.nombres.ilike(f"%{q}%")) | 
            (Persona.nro_documento.ilike(f"%{q}%"))
        )
    
    return [_persona_out(p) for p in q_obj.order_by(Persona.nombres).all()]


@router.get("/buscar-por-cara")
async def buscar_por_cara(db: Session = Depends(get_db)):
    """Placeholder — la identificación por cara se hace vía POST con imagen."""
    return {"detail": "Enviar imagen vía POST /personas/identificar"}


@router.post("/identificar")
def identificar_por_cara(
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Identifica una persona a partir de su imagen facial.

    Extrae el embedding de la imagen, lo compara contra la galería y
    retorna la persona más similar si supera ``FACE_SIMILARITY_THRESHOLD``.
    Usado para autocompletar el formulario de visitante recurrente.

    Args:
        foto: Imagen del rostro a identificar (JPEG o PNG).
        db:   Sesión de base de datos.

    Returns:
        ``{"encontrado": False}`` si no hay match, o dict con ``similitud``
        y ``persona`` si se identificó correctamente.

    Raises:
        HTTPException: 400 si no se detectó rostro en la imagen.
    """
    img_bytes = foto.file.read()
    emb = get_embedding_from_bytes(img_bytes)
    if emb is None:
        raise HTTPException(400, "No se detectó un rostro en la imagen.")

    candidatos = _get_candidatos(db)
    match = find_best_match(emb, candidatos, threshold=FACE_SIMILARITY_THRESHOLD)
    if match is None:
        return {"encontrado": False}

    id_persona, sim = match
    p = db.query(Persona).filter(Persona.id_persona == id_persona).first()
    return {"encontrado": True, "similitud": sim, "persona": _persona_out(p)}


@router.get("/{id_persona}")
def obtener_persona(id_persona: int, db: Session = Depends(get_db)):
    """Retorna el detalle completo de una persona por su ID.

    Args:
        id_persona: Identificador de la persona.
        db:         Sesión de base de datos.

    Returns:
        Diccionario con todos los campos de la persona.

    Raises:
        HTTPException: 404 si la persona no existe.
    """
    p = db.query(Persona).filter(Persona.id_persona == id_persona).first()
    if not p:
        raise HTTPException(404, "Persona no encontrada.")
    return _persona_out(p)


@router.patch("/{id_persona}")
def actualizar_persona(
    id_persona: int,
    body: PersonaUpdate,
    db: Session = Depends(get_db),
):
    """Actualiza el estado de una persona.

    Args:
        id_persona: Identificador de la persona.
        body: Datos a actualizar (activo o estado).
        db: Sesión de base de datos.

    Returns:
        Diccionario con los datos actualizados de la persona.

    Raises:
        HTTPException: 404 si la persona no existe.
    """
    p = db.query(Persona).filter(Persona.id_persona == id_persona).first()
    if not p:
        raise HTTPException(404, "Persona no encontrada.")
    
    # Aceptar tanto activo (bool) como estado (string)
    if body.activo is not None:
        p.activo = body.activo
    elif body.estado is not None:
        p.activo = (body.estado.lower() == "activo")
    
    db.commit()
    db.refresh(p)
    
    return _persona_out(p)


@router.post("/{id_persona}/registros")
def agregar_embedding_registro(
    id_persona: int,
    foto: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Añade un embedding facial de tipo ``'registro'`` a la galería de la persona.

    El frontend llama este endpoint repetidamente durante la captura inicial
    de fotos. Se detiene cuando se alcanza ``MAX_EMBEDDINGS_PER_PERSONA``.

    Args:
        id_persona: Identificador de la persona.
        foto:       Frame capturado durante el registro (JPEG o PNG).
        db:         Sesión de base de datos.

    Returns:
        ``{"ok": True, "n_embeddings": <total>}`` si se guardó correctamente.
        ``{"ok": False, "motivo": ..., "n_embeddings": <total>}`` si no se pudo
        guardar (límite alcanzado o rostro no detectado).

    Raises:
        HTTPException: 404 si la persona no existe.
    """
    p = db.query(Persona).filter(Persona.id_persona == id_persona).first()
    if not p:
        raise HTTPException(404, "Persona no encontrada.")

    # Contar embeddings de registro actuales
    n_actuales = db.query(Registro).filter(
        Registro.id_persona == id_persona,
        Registro.evento == "registro",
    ).count()

    if n_actuales >= MAX_EMBEDDINGS_PER_PERSONA:
        return {"ok": False, "motivo": "limite_alcanzado", "n_embeddings": n_actuales}

    img_bytes = foto.file.read()
    emb = get_embedding_from_bytes(img_bytes)
    if emb is None:
        return {"ok": False, "motivo": "rostro_no_detectado", "n_embeddings": n_actuales}

    reg = Registro(
        id_persona=id_persona,
        evento="registro",
        tipo_acceso=None,
        embedding_facial=embedding_to_bytes(emb),
        similitud=None,
    )
    db.add(reg)
    db.commit()

    return {"ok": True, "n_embeddings": n_actuales + 1}


@router.get("/dentro")
def personas_dentro(db: Session = Depends(get_db)):
    """Retorna la lista de personas que están actualmente dentro del edificio.
    
    Una persona está "dentro" si su último evento de acceso fue una entrada
    y no tiene una salida posterior.
    
    Args:
        db: Sesión de base de datos.
        
    Returns:
        Lista de personas actualmente dentro con su último acceso.
    """
    from datetime import datetime, timezone, timedelta
    from sqlalchemy import func
    
    # Obtener el último registro de acceso por persona
    subq = (
        db.query(
            Registro.id_persona,
            func.max(Registro.fecha).label("ultima_fecha")
        )
        .filter(Registro.evento == "acceso")
        .group_by(Registro.id_persona)
        .subquery()
    )
    
    # Obtener personas cuyo último acceso fue entrada
    registros = (
        db.query(Registro)
        .join(subq, 
            (Registro.id_persona == subq.c.id_persona) & 
            (Registro.fecha == subq.c.ultima_fecha)
        )
        .join(Persona, Registro.id_persona == Persona.id_persona)
        .filter(
            Registro.tipo_acceso == "entrada",
            Persona.activo.is_(True)
        )
        .all()
    )
    
    return [
        {
            "id_persona": r.persona.id_persona,
            "nombre_completo": r.persona.nombres,
            "documento": r.persona.nro_documento,
            "tipo_documento": r.persona.tipo_documento,
            "hora_entrada": r.fecha,
            "similitud": r.similitud,
        }
        for r in registros
    ]


# ── Helper interno ────────────────────────────────────────────────────────────

def _get_candidatos(db: Session) -> list[tuple[int, any]]:
    """Carga la galería de embeddings de referencia de todas las personas activas.

    Args:
        db: Sesión activa de SQLAlchemy.

    Returns:
        Lista de tuplas ``(id_persona, embedding_array)`` con todos los
        embeddings de tipo ``'registro'`` de personas con ``activo=True``.
    """
    rows = (
        db.query(Registro)
        .join(Persona, Registro.id_persona == Persona.id_persona)
        .filter(Persona.activo.is_(True), Registro.evento == "registro")
        .all()
    )
    return [(r.id_persona, bytes_to_embedding(r.embedding_facial)) for r in rows]
