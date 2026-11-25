"""Metadatos y conteo confirmado de fojas, sin almacenar el archivo del reporte."""
import hashlib
import io
import json
from datetime import datetime, timezone

from fastapi import HTTPException
from pypdf import PdfReader
from sqlalchemy import update
from sqlalchemy.orm import joinedload

from .models import Anexos, UnidadResponsable, UserRoles
from .schemas import AnexoResponse

FORMATO_REPORTE = "anexo-carta-v1"
CLAVES_ANEXOS_PDF = frozenset({"PP01", "SGC01", "EO01", "PPA01", "RF18", "RF10"})


def fojas_por_defecto_pdf(anexo):
    return (anexo.clave or "").strip().upper() in CLAVES_ANEXOS_PDF


def consultar_anexo(db, anexo_id, bloquear=False):
    query = db.query(Anexos).populate_existing().options(
        joinedload(Anexos.unidad_responsable).joinedload(UnidadResponsable.padre),
        joinedload(Anexos.creador),
    ).filter(Anexos.id == anexo_id, Anexos.is_deleted.is_not(True))
    if bloquear:
        query = query.with_for_update(of=Anexos)
    anexo = query.first()
    if anexo is None:
        raise HTTPException(404, "Anexo no encontrado")
    return anexo


def revision_reporte(anexo):
    unidad = anexo.unidad_responsable
    padre = unidad.padre if unidad else None
    datos = {"id": anexo.id, "clave": anexo.clave, "datos": anexo.datos,
             "unidad_id": anexo.unidad_responsable_id, "unidad": unidad.nombre if unidad else None,
             "padre_id": padre.id_unidad if padre else None, "padre": padre.nombre if padre else None,
             "actualizado_en": anexo.actualizado_en, "creador_id": anexo.creador_id,
             "creador": anexo.creador.username if anexo.creador else None, "formato": FORMATO_REPORTE}
    return hashlib.sha256(json.dumps(datos, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def reporte_vigente(anexo):
    if fojas_por_defecto_pdf(anexo):
        return True
    return (anexo.fojas_reporte is not None and anexo.reporte_formato == FORMATO_REPORTE
            and anexo.reporte_revision == revision_reporte(anexo))


def resumen_anexo_reporte(anexo):
    datos = AnexoResponse.model_validate(anexo, from_attributes=True).model_dump()
    datos["reporte_vigente"] = reporte_vigente(anexo)
    datos["fojas_por_defecto"] = fojas_por_defecto_pdf(anexo)
    if datos["fojas_por_defecto"]:
        datos["fojas_reporte"] = 1
    return datos


def detalle_anexo_reporte(db, anexo_id):
    anexo = consultar_anexo(db, anexo_id)
    unidad = anexo.unidad_responsable
    padre = unidad.padre if unidad else None
    datos = resumen_anexo_reporte(anexo)
    datos.update(unidad_responsable_nombre=unidad.nombre if unidad else "Unidad no disponible",
                 unidad_padre_id=padre.id_unidad if padre else None, unidad_padre_nombre=padre.nombre if padre else None,
                 creador_nombre=anexo.creador.username if anexo.creador else "Creador no disponible",
                 reporte_revision_actual=revision_reporte(anexo), reporte_formato_actual=FORMATO_REPORTE,
                 reporte_vigente=reporte_vigente(anexo))
    return datos


def registrar_reporte_anexo(db, anexo_id, actor, contenido, revision, formato, content_type):
    try:
        anexo = consultar_anexo(db, anexo_id, bloquear=True)
        if actor.role not in {UserRoles.ADMIN, UserRoles.AUDITOR} and actor.id != anexo.creador_id:
            raise HTTPException(403, "Solo el creador, un administrador o un auditor puede registrar el reporte")
        if fojas_por_defecto_pdf(anexo):
            raise HTTPException(400, "Los anexos de tipo PDF tienen una foja por defecto y no requieren cálculo")
        if formato != FORMATO_REPORTE or revision != revision_reporte(anexo):
            raise HTTPException(409, "El anexo o su formato cambió. Actualiza los datos y genera el reporte nuevamente.")
        if len(contenido) > 25 * 1024 * 1024:
            raise HTTPException(413, "El reporte no puede superar 25 MB")
        if content_type != "application/pdf" or not contenido.startswith(b"%PDF-"):
            raise HTTPException(422, "El reporte debe ser un PDF válido")
        try:
            reader = PdfReader(io.BytesIO(contenido))
            if reader.is_encrypted:
                raise ValueError("PDF cifrado")
            fojas = len(reader.pages)
            if fojas < 1 or not reader.metadata or reader.metadata.subject != revision:
                raise ValueError("Reporte no correspondiente a esta revisión")
        except Exception:
            raise HTTPException(422, "No se pudo verificar el PDF del reporte y su versión de datos")
        db.execute(update(Anexos).where(Anexos.id == anexo_id).values(
            fojas_reporte=fojas, reporte_generado_en=datetime.now(timezone.utc), reporte_revision=revision,
            reporte_formato=formato, actualizado_en=anexo.actualizado_en,
        ))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return detalle_anexo_reporte(db, anexo_id)
