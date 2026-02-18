"""Rutas de reportes. HU-12."""
from datetime import datetime
from io import BytesIO

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.db.models import RegistroAcceso, Persona

router = APIRouter()

MAX_REPORT_ROWS = 2000


def _query_eventos_reporte(
    db: Session,
    fecha_desde: str | None = None,
    fecha_hasta: str | None = None,
    tipo: str | None = None,
    persona_id: int | None = None,
    documento: str | None = None,
    resultado: str | None = None,
):
    """Query de eventos para reporte (misma lógica que events._query_eventos)."""
    q = (
        db.query(RegistroAcceso)
        .join(Persona, RegistroAcceso.id_persona == Persona.id_persona)
        .order_by(RegistroAcceso.fecha_hora.desc())
    )
    if tipo in ("ingreso", "entrada"):
        q = q.filter(RegistroAcceso.tipo_movimiento == "ingreso")
    elif tipo == "salida":
        q = q.filter(RegistroAcceso.tipo_movimiento == "salida")
    if persona_id is not None:
        q = q.filter(RegistroAcceso.id_persona == persona_id)
    if documento and documento.strip():
        q = q.filter(Persona.documento.ilike("%" + documento.strip() + "%"))
    if fecha_desde and fecha_desde.strip():
        try:
            dt = datetime.strptime(fecha_desde.strip()[:10], "%Y-%m-%d")
            q = q.filter(RegistroAcceso.fecha_hora >= dt)
        except ValueError:
            pass
    if fecha_hasta and fecha_hasta.strip():
        try:
            dt = datetime.strptime(fecha_hasta.strip()[:10], "%Y-%m-%d")
            fin_dia = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            q = q.filter(RegistroAcceso.fecha_hora <= fin_dia)
        except ValueError:
            pass
    if resultado and resultado.strip() in ("permitido", "denegado"):
        q = q.filter(RegistroAcceso.resultado == resultado.strip())
    return q


@router.get("/accesos")
def reporte_accesos(
    fecha_desde: str | None = Query(None, description="YYYY-MM-DD"),
    fecha_hasta: str | None = Query(None, description="YYYY-MM-DD"),
    formato: str = Query("csv", description="csv | pdf"),
    tipo: str | None = Query(None),
    persona_id: int | None = Query(None),
    documento: str | None = Query(None),
    resultado: str | None = Query(None),
    db: Session = Depends(get_db),
):
    """
    Genera reporte de accesos en CSV o PDF. HU-12.
    Requiere al menos fecha_desde o fecha_hasta (recomendado ambos).
    Máximo 2000 filas en el detalle.
    """
    q = _query_eventos_reporte(
        db,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo=tipo,
        persona_id=persona_id,
        documento=documento,
        resultado=resultado,
    )
    rows = q.limit(MAX_REPORT_ROWS).all()

    desde_str = (fecha_desde or "")[:10] or "inicio"
    hasta_str = (fecha_hasta or "")[:10] or "fin"
    filename_base = f"reporte-accesos-{desde_str}-{hasta_str}"

    if formato.lower() == "pdf":
        try:
            from fpdf import FPDF
        except ImportError:
            return Response(
                content=b"PDF no disponible: instale fpdf2",
                status_code=501,
                media_type="text/plain",
            )
        total_all = len(rows)
        permitidos = sum(1 for r in rows if r.resultado == "permitido")
        denegados = sum(1 for r in rows if r.resultado == "denegado")
        personas_unicas = len({r.id_persona for r in rows})

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Helvetica", size=14)
        pdf.cell(0, 10, "Reporte de accesos - SCA-EMPX", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 6, f"Periodo: {desde_str} a {hasta_str}", ln=True)
        pdf.cell(0, 6, f"Total eventos: {total_all}  |  Permitidos: {permitidos}  |  Denegados: {denegados}  |  Personas unicas (muestra): {personas_unicas}", ln=True)
        pdf.ln(4)

        if rows:
            table_data = [("Fecha/hora", "Persona", "Tipo", "Resultado")]
            for r in rows[:100]:  # max 100 rows in PDF for size
                nombre = (r.persona.nombre_completo if r.persona else "") or ""
                table_data.append((
                    r.fecha_hora.strftime("%Y-%m-%d %H:%M") if r.fecha_hora else "",
                    nombre[:30],
                    r.tipo_movimiento or "",
                    r.resultado or "",
                ))
            if len(rows) > 100:
                table_data.append(("...", f"(y {len(rows) - 100} registros mas)", "", ""))

            pdf.set_font("Helvetica", size=8)
            with pdf.table() as table:
                for data_row in table_data:
                    row = table.row()
                    for datum in data_row:
                        row.cell(str(datum))

        buf = BytesIO()
        pdf.output(buf)
        buf.seek(0)
        return Response(
            content=buf.read(),
            media_type="application/pdf",
            headers={"Content-Disposition": f'attachment; filename="{filename_base}.pdf"'},
        )

    # CSV
    lines = ["id_registro;id_persona;nombre_completo;tipo_movimiento;fecha_hora;resultado;metodo_identificacion"]
    for r in rows:
        nombre = (r.persona.nombre_completo if r.persona else "") or ""
        nombre = nombre.replace(";", ",")
        lines.append(
            f"{r.id_registro};{r.id_persona};{nombre};{r.tipo_movimiento};{r.fecha_hora.isoformat() if r.fecha_hora else ''};{r.resultado};{r.metodo_identificacion}"
        )
    return Response(
        content="\n".join(lines),
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{filename_base}.csv"',
        },
    )
