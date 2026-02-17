"""Rutas personas (empleados y visitantes). HU-01, HU-02, HU-03, HU-10."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.persona_service import registrar_empleado, registrar_visitante
from backend.app.schemas.persona import PersonaRegistroResponse, PersonaListItem

router = APIRouter()

TIPO_EMPLEADO = "empleado_propio"
TIPO_VISITANTE = "visitante_temporal"


def _map_registro_errors(e: ValueError) -> None:
    msg = str(e)
    if msg == "documento_duplicado":
        raise HTTPException(status_code=409, detail="Ya existe una persona con ese documento.")
    if msg == "rostro_no_detectado":
        raise HTTPException(
            status_code=400,
            detail="No se detectó un rostro en la imagen. Use una foto con un único rostro visible.",
        )
    if msg == "foto_requerida":
        raise HTTPException(status_code=400, detail="Se requiere una foto.")
    if msg == "tipo_persona_no_configurado":
        raise HTTPException(
            status_code=500,
            detail="Tipo de persona no configurado. Ejecute init_db.",
        )
    raise HTTPException(status_code=400, detail=msg)


@router.get("/", response_model=list[PersonaListItem])
def listar_personas(
    tipo: str | None = None,
    db: Session = Depends(get_db),
):
    """
    Lista personas. tipo=empleado_propio|empleado: solo empleados. tipo=visitante_temporal|visitante: solo visitantes. HU-03, HU-04.
    """
    from backend.app.db.models import Persona, TipoPersona
    q = db.query(Persona).join(TipoPersona, Persona.id_tipo_persona == TipoPersona.id_tipo_persona)
    if tipo in ("empleado_propio", "empleado"):
        q = q.filter(TipoPersona.nombre_tipo == "empleado_propio")
    elif tipo in ("visitante_temporal", "visitante"):
        q = q.filter(TipoPersona.nombre_tipo == "visitante_temporal")
    q = q.filter(Persona.estado == "activo")
    personas = q.order_by(Persona.nombre_completo).all()
    return [PersonaListItem(id_persona=p.id_persona, nombre_completo=p.nombre_completo, documento=p.documento) for p in personas]


@router.post("/", response_model=PersonaRegistroResponse)
def registrar_persona(
    nombre_completo: str = Form(..., min_length=1),
    documento: str = Form(..., min_length=1),
    tipo: str = Form(TIPO_EMPLEADO, description="empleado_propio | visitante_temporal"),
    tipo_documento: str = Form("CC"),
    cargo: str = Form(""),
    area: str = Form(""),
    empresa: str = Form(""),
    motivo_visita: str = Form(""),
    id_empleado_visitado: str = Form(""),
    foto: UploadFile = File(..., description="Foto (rostro visible, JPEG/PNG)"),
    db: Session = Depends(get_db),
):
    """
    Registra persona (empleado o visitante) con foto. Genera embedding Facenet.
    Para visitante: enviar tipo=visitante_temporal, empresa y motivo_visita. Opcional id_empleado_visitado.
    Documento único (409). Requiere un rostro en la foto (400 si no se detecta).
    """
    if not foto.content_type or not foto.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (JPEG, PNG, etc.)")

    image_bytes = foto.file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Imagen vacía")

    tipo = (tipo or TIPO_EMPLEADO).strip()
    calidad_resp: float | None = None
    if tipo == TIPO_VISITANTE:
        if not (empresa or "").strip():
            raise HTTPException(status_code=400, detail="Para visitante se requiere empresa.")
        if not (motivo_visita or "").strip():
            raise HTTPException(status_code=400, detail="Para visitante se requiere motivo_visita.")
        try:
            persona, reco, _ = registrar_visitante(
                db,
                nombre_completo=nombre_completo,
                documento=documento,
                empresa=empresa.strip(),
                motivo_visita=motivo_visita.strip(),
                tipo_documento=tipo_documento or "CC",
                id_empleado_visitado=int(id_empleado_visitado) if (id_empleado_visitado or "").strip().isdigit() else None,
                image_bytes=image_bytes,
            )
        except ValueError as e:
            _map_registro_errors(e)
    else:
        try:
            persona, reco, calidad_resp = registrar_empleado(
                db,
                nombre_completo=nombre_completo,
                documento=documento,
                cargo=cargo or None,
                area=area or None,
                tipo_documento=tipo_documento or "CC",
                image_bytes=image_bytes,
            )
        except ValueError as e:
            _map_registro_errors(e)

    return PersonaRegistroResponse(
        id_persona=persona.id_persona,
        nombre_completo=persona.nombre_completo,
        documento=persona.documento,
        estado=persona.estado,
        calidad_embedding=calidad_resp,
    )


@router.patch("/{persona_id:int}")
def actualizar_persona(persona_id: int):
    return {"message": f"Actualizar persona {persona_id} (por implementar)"}
