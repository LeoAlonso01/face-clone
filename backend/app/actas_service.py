"""Persistencia de actas y asociación atómica de anexos pendientes."""
import hashlib
import json

from fastapi import HTTPException
from sqlalchemy import or_
from sqlalchemy.orm import selectinload

from .models import ActaEntregaRecepcion, Anexos, UnidadResponsable, User, UserRoles



ESTADOS_ACTA_EDITABLES = {"Borrador", "Pendiente", "Revisión"}


def validar_edicion_acta(db, acta, actor, cambios):
    es_gestor = actor.role in {UserRoles.ADMIN, UserRoles.AUDITOR}
    es_creador = actor.role == UserRoles.USER and acta.creador_id is not None and actor.id == acta.creador_id
    if not (es_gestor or es_creador):
        raise HTTPException(403, "No tienes permiso para editar esta acta")
    if acta.estado not in ESTADOS_ACTA_EDITABLES:
        raise HTTPException(400, "El acta está cerrada y no admite modificaciones")
    if "estado" in cambios:
        permitidos = {"Pendiente", "Revisión", "Completada"}
        if acta.estado == "Borrador":
            permitidos.add("Borrador")
        if cambios["estado"] not in permitidos:
            raise HTTPException(400, "Selecciona un estado válido: Pendiente, Revisión o Completada")
    for campo in ("entrante", "saliente"):
        if campo in cambios and (not isinstance(cambios[campo], str) or not cambios[campo].strip()):
            raise HTTPException(400, "Captura el nombre completo de los funcionarios")
    cambia_unidad = "unidad_responsable" in cambios and cambios["unidad_responsable"] != acta.unidad_responsable
    cambia_saliente = "saliente_id" in cambios and cambios["saliente_id"] != acta.saliente_id
    if cambia_unidad or cambia_saliente:
        tiene_anexos = db.query(Anexos.id).filter(Anexos.acta_id == acta.id, Anexos.is_deleted.is_not(True)).first() is not None
        if tiene_anexos:
            raise HTTPException(409, "El acta tiene anexos asociados: no puedes cambiar la unidad ni la cuenta del saliente")
    if cambia_unidad:
        if not db.query(UnidadResponsable.id_unidad).filter(UnidadResponsable.id_unidad == cambios["unidad_responsable"]).first():
            raise HTTPException(400, "La unidad responsable no existe")
    if "folio" in cambios and cambios["folio"] != acta.folio:
        if not isinstance(cambios["folio"], str) or not cambios["folio"].strip():
            raise HTTPException(400, "Captura el folio del acta")
        repetido = db.query(ActaEntregaRecepcion.id).filter(ActaEntregaRecepcion.folio == cambios["folio"], ActaEntregaRecepcion.id != acta.id).first()
        if repetido:
            raise HTTPException(409, "Ya existe un acta con ese folio")

def preparar_participantes(db, datos):
    """Conservar el nombre del acta, independiente del username de la cuenta."""
    datos = dict(datos)
    if any(key in datos and datos[key] is None for key in ("comisiones", "comisionados")):
        raise HTTPException(400, "Comisiones y comisionados deben ser listas")
    comisiones = datos.get("comisiones")
    if comisiones is not None:
        ids = [item["usuario_id"] for item in comisiones if item.get("usuario_id") is not None]
        if len(ids) != len(set(ids)):
            raise HTTPException(400, "No se puede repetir un usuario entre los comisionados")
        if "comisionados" in datos and set(datos["comisionados"] or []) != set(ids):
            raise HTTPException(400, "Los comisionados no coinciden con el detalle de comisiones")
        datos["comisionados"] = ids
        # Una lista vacía enviada explícitamente permite quitar todos los comisionados.
        datos["comisionado"] = ", ".join(item["nombre"].strip() for item in comisiones) if comisiones else datos.get("comisionado", "")
        datos["comisiones"] = [dict(item, **({
            "oficio_comision": datos.get("oficio_comision"),
            "fecha_oficio_comision": datos.get("fecha_oficio_comision"),
        } if item.get("mismo_oficio", True) else {})) for item in comisiones]

    for campo, roles in (
        ("entrante_id", None),
        ("saliente_id", {UserRoles.USER}),
    ):
        user_id = datos.get(campo)
        if user_id is not None:
            _validar_usuario(db, user_id, roles)
            nombre = datos.get(campo.removesuffix("_id"))
            if not nombre or not nombre.strip():
                raise HTTPException(400, "Captura el nombre completo de los funcionarios seleccionados")
    for user_id in datos.get("comisionados") or []:
        _validar_usuario(db, user_id, {UserRoles.ADMIN, UserRoles.AUDITOR})
    return datos


def _validar_usuario(db, user_id, roles):
    user = db.query(User).filter(User.id == user_id, User.is_deleted.is_not(True)).first()
    if user is None or (roles is not None and user.role not in roles):
        raise HTTPException(400, f"Usuario {user_id} inexistente, eliminado o con rol no permitido")


def anexos_pendientes(db, unidad_id, creador_id):
    return db.query(Anexos).populate_existing().filter(
        Anexos.creador_id == creador_id,
        Anexos.unidad_responsable_id == unidad_id,
        Anexos.is_deleted.is_not(True),
        or_(Anexos.acta_id.is_(None), Anexos.acta_id == 0),
    ).order_by(Anexos.id)


def revision_anexos(anexos, unidad_id, creador_id):
    snapshot = {"unidad": unidad_id, "creador": creador_id, "anexos": [
        {"id": item.id, "clave": item.clave, "estado": item.estado,
         "fecha_creacion": item.fecha_creacion, "actualizado_en": item.actualizado_en,
         "datos": item.datos} for item in anexos
    ]}
    return hashlib.sha256(json.dumps(snapshot, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")).hexdigest()


def creador_anexos_para_acta(db, actor_id, saliente_id=None):
    origen_id = saliente_id if saliente_id is not None else actor_id
    actor = db.query(User).filter(User.id == actor_id, User.is_deleted.is_not(True)).first()
    if actor is None:
        raise HTTPException(401, "Usuario autenticado no disponible")
    if origen_id != actor_id and actor.role not in {UserRoles.ADMIN, UserRoles.AUDITOR}:
        raise HTTPException(403, "No tienes permiso para asociar anexos de otro funcionario")
    if saliente_id is not None:
        _validar_usuario(db, saliente_id, {UserRoles.USER})
    return origen_id


def vista_previa_acta(db, unidad_id, actor_id, saliente_id=None):
    creador_id = creador_anexos_para_acta(db, actor_id, saliente_id)
    unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad_id).first()
    if unidad is None:
        raise HTTPException(400, f"Unidad responsable con ID {unidad_id} no existe")
    anexos = anexos_pendientes(db, unidad_id, creador_id).all()
    return {
        "unidad_responsable": unidad_id, "unidad_nombre": unidad.nombre,
        "anexos_creador_id": creador_id,
        "anexos_creador_usuario": db.get(User, creador_id).username,
        "anexos_origen": "saliente" if saliente_id is not None else "usuario_autenticado",
        "total": len(anexos), "anexos_revision": revision_anexos(anexos, unidad_id, creador_id),
        "anexos": [{"id": item.id, "clave": item.clave, "estado": item.estado,
                    "fecha_creacion": item.fecha_creacion, "filas": len(item.datos or [])} for item in anexos],
    }


def crear_acta_con_anexos(db, acta, creador_id):
    """Un solo commit; el UPDATE no puede reclamar anexos ya asociados."""
    try:
        unidad = db.query(UnidadResponsable).filter(
            UnidadResponsable.id_unidad == acta.unidad_responsable
        ).first()
        if unidad is None:
            raise HTTPException(400, f"Unidad responsable con ID {acta.unidad_responsable} no existe")
        if db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.folio == acta.folio).first():
            raise HTTPException(400, f"Ya existe un acta con el folio {acta.folio}")

        datos = acta.model_dump(exclude_unset=True)
        datos["estado"] = acta.estado or "Pendiente"
        revision = datos.pop("anexos_revision", None)
        anexos_creador_id = creador_anexos_para_acta(db, creador_id, acta.saliente_id)
        ids_confirmados = None
        if revision is not None:
            candidatos = anexos_pendientes(db, acta.unidad_responsable, anexos_creador_id).with_for_update(of=Anexos).all()
            if revision != revision_anexos(candidatos, acta.unidad_responsable, anexos_creador_id):
                raise HTTPException(409, "La lista de anexos cambió. Revisa la vista previa y confirma nuevamente.")
            ids_confirmados = [item.id for item in candidatos]
        datos = preparar_participantes(db, datos)
        db_acta = ActaEntregaRecepcion(**datos, creador_id=creador_id)
        db.add(db_acta)
        db.flush()  # Obtener ID sin confirmar todavía la creación.
        pendientes = anexos_pendientes(db, acta.unidad_responsable, anexos_creador_id).order_by(None)
        if ids_confirmados is not None:
            pendientes = pendientes.filter(Anexos.id.in_(ids_confirmados))
        vinculados = pendientes.update({Anexos.acta_id: db_acta.id}, synchronize_session=False)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return cargar_acta(db, db_acta.id), vinculados


def cargar_acta(db, acta_id):
    # Reemplazar relaciones que una consulta anterior pudiera haber cargado vacías.
    return db.query(ActaEntregaRecepcion).populate_existing().options(
        selectinload(ActaEntregaRecepcion.anexos)
    ).filter(ActaEntregaRecepcion.id == acta_id).one()


def datos_acta_documento(db, acta_id):
    acta = db.query(ActaEntregaRecepcion).populate_existing().options(
        selectinload(ActaEntregaRecepcion.unidad)
    ).filter(ActaEntregaRecepcion.id == acta_id).first()
    if acta is None:
        raise HTTPException(404, "Acta no encontrada")
    if acta.unidad is None:
        raise HTTPException(400, "No se encontró la unidad responsable del acta")
    datos = {column.name: getattr(acta, column.name) for column in ActaEntregaRecepcion.__table__.columns}
    datos["unidad_nombre"] = acta.unidad.nombre
    anexos = db.query(Anexos).populate_existing().filter(
        Anexos.acta_id == acta_id, Anexos.is_deleted.is_not(True)
    ).order_by(Anexos.id).all()
    from .anexo_reportes import resumen_anexo_reporte
    datos["anexos"] = []
    for anexo in anexos:
        item = resumen_anexo_reporte(anexo)
        if not item["reporte_vigente"]:
            item["fojas_reporte"] = None
        datos["anexos"].append(item)
    return datos
