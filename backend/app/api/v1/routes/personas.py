"""Rutas personas (empleados y visitantes). HU-01, HU-02, HU-03, HU-10."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.persona_service import registrar_empleado
from backend.app.schemas.persona import PersonaRegistroResponse

router = APIRouter()


@router.get("/")
def listar_personas():
    return {"message": "Listado de personas (por implementar)"}


@router.post("/", response_model=PersonaRegistroResponse)
def registrar_persona(
    nombre_completo: str = Form(..., min_length=1),
    documento: str = Form(..., min_length=1),
    cargo: str = Form(""),
    area: str = Form(""),
    tipo_documento: str = Form("CC"),
    foto: UploadFile = File(..., description="Foto del empleado (rostro visible, JPEG/PNG)"),
    db: Session = Depends(get_db),
):
    """
    Registra un empleado con foto. Genera embedding facial (Facenet) y persiste persona + reconocimiento_facial.
    Documento debe ser único (409 si ya existe). Requiere exactamente un rostro en la foto (400 si no se detecta).
    """
    if not foto.content_type or not foto.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="El archivo debe ser una imagen (JPEG, PNG, etc.)")

    image_bytes = foto.file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Imagen vacía")

    try:
        persona, reco, calidad = registrar_empleado(
            db,
            nombre_completo=nombre_completo,
            documento=documento,
            cargo=cargo or None,
            area=area or None,
            tipo_documento=tipo_documento or "CC",
            image_bytes=image_bytes,
        )
    except ValueError as e:
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
                detail="Tipo de persona 'empleado_propio' no configurado. Ejecute init_db.",
            )
        raise HTTPException(status_code=400, detail=msg)

    return PersonaRegistroResponse(
        id_persona=persona.id_persona,
        nombre_completo=persona.nombre_completo,
        documento=persona.documento,
        estado=persona.estado,
        calidad_embedding=calidad,
    )


@router.patch("/{persona_id:int}")
def actualizar_persona(persona_id: int):
    return {"message": f"Actualizar persona {persona_id} (por implementar)"}
