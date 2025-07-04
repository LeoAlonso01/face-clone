from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from .database import Base
import datetime
from sqlalchemy import Boolean
from enum import Enum as PyEnum
from pydantic import BaseModel

class UserRoles(PyEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    AUDIROR = "AUDITOR"

class UserResponse(BaseModel):
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
        orm_mode = True

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    is_deleted = Column(Boolean, default=False) # Soft delete
    role = Column(Enum(UserRoles), default=UserRoles.USER, nullable=True)
    posts = relationship("Post", back_populates="owner")
    unidades_a_cargo = relationship("UnidadResponsable", back_populates="usuario_responsable")

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime)

    owner = relationship("User", back_populates="posts")

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
    responsable = Column(Integer, ForeignKey('users.id'), nullable=True)  # Modificado
    tipo_unidad = Column(String(50))
    fecha_creacion = Column(DateTime, default=datetime.datetime.now)
    fecha_cambio = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    # columna de jerarquía para relacionar unidades responsables
    unidad_padre_id = Column(Integer, ForeignKey("unidades_responsables.id_unidad"), nullable=True)
    # Relacion
    dependientes = relationship("UnidadResponsable", back_populates="padre")
    # Relación con UnidadResponsable
    padre = relationship("UnidadResponsable", remote_side=[id_unidad], back_populates="dependientes")
    # Relación con User
    usuario_responsable = relationship("User", back_populates="unidades_a_cargo") # Relación con User