from sqlalchemy import JSON, Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime, date, time
from sqlalchemy import ForeignKey
from sqlalchemy.sql import func
from typing import Optional
from sqlalchemy import Boolean
from enum import Enum as PyEnum
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Date, Time, DateTime, Text

def utcnow():
    return datetime.now() 

class UserRoles(PyEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"

""" class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    role: UserRoles | None
    is_deleted: bool

    class Config:
        orm_mode = True

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: UserRoles

    class Config:
        orm_mode = True

# class UserUpdate(BaseModel):
class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None
    role: UserRoles | None = None
    is_deleted: bool | None = None

    class Config:
        orm_mode = True """

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    is_deleted = Column(Boolean, default=False) # Soft delete
    role = Column(Enum(UserRoles), default=UserRoles.USER, nullable=True)
    # relaciones
    unidad = relationship("UnidadResponsable", back_populates="usuario_responsable", uselist=False)
    # recuperacion de contraseña
    reset_token = Column(String, nullable=True)
    reset_token_expiration = Column(DateTime, nullable=True)


# This is the model for Unidad Responsable
# It represents a responsible unit in the system, such as a department or office.
class UnidadResponsable(Base):
    __tablename__ = "unidades_responsables"

    id_unidad = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(255), nullable=False)
    telefono = Column(String(20))
    domicilio = Column(String(255))
    municipio = Column(String(100))
    localidad = Column(String(100))
    codigo_postal = Column(String(10))
    rfc = Column(String(13))
    correo_electronico = Column(String(100))

    responsable = Column(Integer, ForeignKey("users.id"))
    tipo_unidad = Column(String(50))
    fecha_creacion = Column(DateTime, server_default=func.now())
    fecha_cambio = Column(DateTime, server_default=func.now(), onupdate=func.now())
    # columna de jerarquía para relacionar unidades responsables
    unidad_padre_id = Column(Integer, ForeignKey("unidades_responsables.id_unidad"), nullable=True)
    # Relacion
    dependientes = relationship("UnidadResponsable", back_populates="padre")
    # Relación con UnidadResponsable
    padre = relationship("UnidadResponsable", remote_side=[id_unidad], back_populates="dependientes")
    # Relación con User
    usuario_responsable = relationship(
        "User", foreign_keys=[responsable],
        back_populates="unidad",
        lazy="joined")
    actas = relationship("ActaEntregaRecepcion", back_populates="unidad")

    # 👉 RELACIÓN CON ANEXOS (esto es lo nuevo)
    anexos = relationship("Anexos", back_populates="unidad_responsable")

    class Config:
        orm_mode = True


# esquema para el acta entrega-recepción
class ActaEntregaRecepcion(Base):
    __tablename__ = "acta_entrega_recepcion"

    id = Column(Integer, primary_key=True, index=True)
    unidad_responsable = Column(Integer, ForeignKey("unidades_responsables.id_unidad"), nullable=False)
    folio = Column(String)
    fecha = Column(String)
    hora = Column(String)
    comisionado = Column(String)
    oficio_comision = Column(String, nullable=True)
    fecha_oficio_comision = Column(String, nullable=True)
    entrante = Column(String)
    ine_entrante = Column(String, nullable=True)
    fecha_inicio_labores = Column(String, nullable=True)
    nombramiento = Column(String, nullable=True)
    fecha_nombramiento = Column(String, nullable=True)
    asignacion = Column(String, nullable=True)
    asignado_por = Column(String, nullable=True)
    domicilio_entrante = Column(String, nullable=True)
    telefono_entrante = Column(String, nullable=True)
    saliente = Column(String, nullable=True)
    fecha_fin_labores = Column(String, nullable=True)
    testigo_entrante = Column(String, nullable=True)
    ine_testigo_entrante = Column(String, nullable=True)
    testigo_saliente = Column(String, nullable=True)
    ine_testigo_saliente = Column(String, nullable=True)
    fecha_cierre_acta = Column(String, nullable=True)
    hora_cierre_acta = Column(String, nullable=True)
    observaciones = Column(Text, nullable=True)
    estado = Column(String, nullable=True)
    creado_en = Column(DateTime, server_default=func.now())
    actualizado_en = Column(DateTime, server_default=func.now(), onupdate=func.now())
    # 👉 RELACIÓN CON ANEXOS (esto es lo nuevo)
    anexos = relationship(
        "Anexos", 
        back_populates="acta", 
        lazy="selectin", 
        cascade="all, delete-orphan"
        )  

    # relacion con unidades responsables
    unidad = relationship("UnidadResponsable", back_populates="actas")

class Anexos(Base):             
    __tablename__ = "anexos"

    id = Column(Integer, primary_key=True, index=True)
    clave = Column(String)
    creador_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    fecha_creacion = Column(DateTime, default=utcnow)
    datos = Column(JSON, nullable=False)
    estado = Column(String, nullable=False)
    unidad_responsable_id = Column(Integer, ForeignKey("unidades_responsables.id_unidad"), nullable=False)
    creado_en = Column(Date, default=date.today)
    actualizado_en = Column(Date, default=date.today, onupdate=date.today)
    is_deleted = Column(Boolean, default=False)  # Soft delete
    # Relacion con Unidad Responsable
    unidad_responsable = relationship("UnidadResponsable", back_populates="anexos")
    
    # Relación con Acta
    acta_id = Column(Integer, ForeignKey("acta_entrega_recepcion.id"), nullable=True)
    acta = relationship("ActaEntregaRecepcion", back_populates="anexos")



