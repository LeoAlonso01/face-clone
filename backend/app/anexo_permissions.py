"""Assignment management and capture authorization. No implicit migrations or commits."""
import os
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field, StrictStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import Boolean, CheckConstraint, Column, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint, select
from sqlalchemy.orm import Session

from .database import Base, get_db
from .models import Anexos, User, UserRoles
from .auth import get_admin_user, get_current_user


class AnexoCatalogo(Base):
    __tablename__ = "anexo_catalogo"
    clave = Column(String(30), primary_key=True)
    categoria_id = Column(String(30), nullable=False)
    categoria = Column(String(200), nullable=False)
    descripcion = Column(String(500), nullable=False)
    activo = Column(Boolean, nullable=False, default=True, server_default="true")


class AnexoConfig(Base):
    __tablename__ = "usuario_anexo_config"
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    revision = Column(Integer, nullable=False)
    confirmado_por = Column(Integer, ForeignKey("users.id"), nullable=False)
    confirmado_en = Column(DateTime(timezone=True), nullable=False)
    __table_args__ = (CheckConstraint("revision > 0", name="ck_anexo_config_revision"),)


class AnexoPermiso(Base):
    __tablename__ = "usuario_anexo_permiso"
    user_id = Column(Integer, ForeignKey("usuario_anexo_config.user_id"), primary_key=True)
    clave = Column(String(30), ForeignKey("anexo_catalogo.clave"), primary_key=True)


class AnexoPermisoHistorial(Base):
    __tablename__ = "usuario_anexo_historial"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    revision = Column(Integer, nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fecha = Column(DateTime(timezone=True), nullable=False)
    anteriores = Column(JSON, nullable=False)
    nuevas = Column(JSON, nullable=False)
    motivo = Column(String(500), nullable=False)
    __table_args__ = (UniqueConstraint("user_id", "revision", name="uq_anexo_historial_revision"),)


PERMISSION_TABLES = {"anexo_catalogo", "usuario_anexo_config", "usuario_anexo_permiso", "usuario_anexo_historial"}
router = APIRouter(prefix="/permisos-anexos", tags=["Permisos de anexos"])


class PermissionSettings(BaseSettings):
    ANEXOS_PERMISOS_ESTRICTOS: bool = False
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


_settings = PermissionSettings()


class ConfigUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    revision: int = Field(ge=0, strict=True)
    claves: list[StrictStr] = Field(max_length=500)
    motivo: str = Field(min_length=5, max_length=500)


def normalizar(clave: str) -> str:
    import re
    return re.sub(r"^RRH(?=\d)", "RH", clave.strip().upper())


def estricto() -> bool:
    return os.getenv("ANEXOS_PERMISOS_ESTRICTOS", str(_settings.ANEXOS_PERMISOS_ESTRICTOS)).lower() in {"true", "1", "yes"}


def usuario_vigente(user: User):
    if user.is_deleted:
        raise HTTPException(403, "El usuario está dado de baja")


def bloquear_usuario(db: Session, user_id: int) -> User:
    # Serializa asignaciones y capturas, también cuando aún no hay configuración.
    user = db.query(User).filter(User.id == user_id).with_for_update(of=User).first()
    if user is None or user.is_deleted:
        raise HTTPException(404, "Usuario no encontrado")
    return user


def configuracion(db: Session, user_id: int) -> dict:
    config = db.get(AnexoConfig, user_id, populate_existing=True)
    claves = sorted(db.scalars(select(AnexoPermiso.clave).where(AnexoPermiso.user_id == user_id)).all())
    return {"user_id": user_id, "configurado": config is not None,
            "revision": config.revision if config else 0, "claves": claves,
            "confirmado_en": config.confirmado_en if config else None,
            "confirmado_por": config.confirmado_por if config else None,
            "modo": "estricto" if estricto() else "gradual"}


def validar_captura(db: Session, actor: User, clave: str, anexo: Anexos | None = None) -> str:
    usuario_vigente(actor)
    if actor.role not in (UserRoles.USER, UserRoles.ADMIN):
        raise HTTPException(403, "Tu rol no permite capturar anexos")
    if anexo is not None and actor.role != UserRoles.ADMIN and anexo.creador_id != actor.id:
        raise HTTPException(403, "Solo el creador o un ADMIN puede modificar el anexo")
    bloquear_usuario(db, actor.id)
    clave = normalizar(clave)
    catalogo = db.get(AnexoCatalogo, clave)
    if catalogo is None or not catalogo.activo:
        raise HTTPException(422, "Clave desconocida o inactiva en el catálogo de anexos")
    config = db.get(AnexoConfig, actor.id, populate_existing=True)
    # Una configuración confirmada también limita la captura de ADMIN.
    # Administrar permisos y capturar son autorizaciones independientes.
    if config is not None or (estricto() and actor.role != UserRoles.ADMIN):
        permiso = db.get(AnexoPermiso, (actor.id, clave))
        if permiso is None:
            raise HTTPException(403, "Tu configuración cambió o no tienes habilitada esta clave. Consulta al administrador.")
    return clave


@router.get("/catalogo")
def catalogo(db: Session = Depends(get_db), actor: User = Depends(get_current_user)):
    usuario_vigente(actor)
    return db.query(AnexoCatalogo).filter(AnexoCatalogo.activo.is_(True)).order_by(AnexoCatalogo.clave).all()


@router.get("/mios")
def mios(db: Session = Depends(get_db), actor: User = Depends(get_current_user)):
    usuario_vigente(actor)
    data = configuracion(db, actor.id)
    data["sin_restriccion"] = not data["configurado"] and (actor.role == UserRoles.ADMIN or not estricto())
    if actor.role not in (UserRoles.USER, UserRoles.ADMIN):
        data["sin_restriccion"] = False
        data["claves"] = []
    return data


@router.get("/usuarios")
def usuarios(db: Session = Depends(get_db), actor: User = Depends(get_admin_user)):
    usuario_vigente(actor)
    return [{"id": user.id, "username": user.username} for user in
            db.query(User).filter(User.is_deleted.is_(False)).order_by(User.username).all()]


def acceso_usuario(db: Session, actor: User, user_id: int):
    usuario_vigente(actor)
    if actor.id != user_id and actor.role != UserRoles.ADMIN:
        raise HTTPException(403, "No puedes consultar la configuración de otro usuario")
    user = db.get(User, user_id)
    if user is None or user.is_deleted:
        raise HTTPException(404, "Usuario no encontrado")


@router.get("/usuarios/{user_id}")
def obtener_config(user_id: int, db: Session = Depends(get_db), actor: User = Depends(get_current_user)):
    acceso_usuario(db, actor, user_id)
    return configuracion(db, user_id)


@router.get("/usuarios/{user_id}/propuesta")
def propuesta(user_id: int, db: Session = Depends(get_db), actor: User = Depends(get_admin_user)):
    acceso_usuario(db, actor, user_id)
    existentes = {normalizar(clave) for clave in db.scalars(select(Anexos.clave).where(
        Anexos.creador_id == user_id, Anexos.is_deleted.is_(False))).all() if clave}
    validas = set(db.scalars(select(AnexoCatalogo.clave).where(AnexoCatalogo.activo.is_(True))).all())
    return {"claves": sorted(existentes & validas), "desconocidas": sorted(existentes - validas)}


@router.put("/usuarios/{user_id}")
def guardar_config(user_id: int, payload: ConfigUpdate, db: Session = Depends(get_db), actor: User = Depends(get_admin_user)):
    usuario_vigente(actor)
    bloquear_usuario(db, user_id)
    actual = configuracion(db, user_id)
    if actual["revision"] != payload.revision:
        raise HTTPException(409, "Otro administrador modificó la configuración. Recarga antes de guardar.")
    nuevas = sorted(set(normalizar(clave) for clave in payload.claves))
    validas = set(db.scalars(select(AnexoCatalogo.clave).where(AnexoCatalogo.activo.is_(True))).all())
    if set(nuevas) - validas:
        raise HTTPException(422, "La configuración contiene claves desconocidas o inactivas")
    motivo = payload.motivo.strip()
    if len(motivo) < 5:
        raise HTTPException(422, "Explica el motivo del cambio (mínimo 5 caracteres)")
    fecha = datetime.now(timezone.utc)
    revision = actual["revision"] + 1
    try:
        config = db.get(AnexoConfig, user_id)
        if config is None:
            config = AnexoConfig(user_id=user_id)
            db.add(config)
        config.revision = revision
        config.confirmado_por = actor.id
        config.confirmado_en = fecha
        db.flush()
        db.query(AnexoPermiso).filter(AnexoPermiso.user_id == user_id).delete(synchronize_session=False)
        db.add_all([AnexoPermiso(user_id=user_id, clave=clave) for clave in nuevas])
        db.add(AnexoPermisoHistorial(user_id=user_id, revision=revision, actor_id=actor.id,
                                   fecha=fecha, anteriores=actual["claves"], nuevas=nuevas, motivo=motivo))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return configuracion(db, user_id)


@router.get("/usuarios/{user_id}/historial")
def historial(user_id: int, skip: int = 0, limit: int = 20, db: Session = Depends(get_db), actor: User = Depends(get_admin_user)):
    acceso_usuario(db, actor, user_id)
    return db.query(AnexoPermisoHistorial).filter(AnexoPermisoHistorial.user_id == user_id).order_by(
        AnexoPermisoHistorial.revision.desc()).offset(max(0, skip)).limit(max(1, min(limit, 100))).all()
