# schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class UserRoles(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"

# Esquema base para usuario
class UserBase(BaseModel):
    username: str
    email: str
    role: UserRoles = UserRoles.USER
    nombre: str
    unidad_responsable_id: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None

# Esquema para creación de usuario (incluye password)
class UserCreate(UserBase):
    password: str

# Esquema para respuesta (sin password)
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    is_deleted: bool

    class Config:
        orm_mode = True

# Esquema para actualización (todos los campos opcionales)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRoles] = None
    nombre: Optional[str] = None
    unidad_responsable_id: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None

# Esquema para Unidad Responsable
# Es una unidad responsable en el sistema, como un departamento u oficina.
class UnidadResponsableBase(BaseModel):
    nombre: str
    telefono: Optional[str] = None
    domicilio: Optional[str] = None
    municipio: Optional[str] = None
    localidad: Optional[str] = None
    codigo_postal: Optional[str] = None
    rfc: Optional[str] = None
    correo_electronico: Optional[str] = None
    responsable: Optional[int] = None  # Ahora es ID de usuario
    tipo_unidad: Optional[str] = None
    unidad_padre_id: Optional[int] = None  # ID de la unidad responsable padre

    class Config:
        orm_mode = True

# Esquema para creación de Unidad Responsable
class UnidadResponsableCreate(UnidadResponsableBase):
    pass

# Esquema para actualización de Unidad Responsable
class UnidadResponsableUpdate(UnidadResponsableBase):
    pass

# Esquema para respuesta de Unidad Responsable
class UnidadResponsableResponse(UnidadResponsableBase):
    id_unidad: int
    nombre: str
    fecha_creacion: Optional[datetime] = None
    fecha_cambio: Optional[datetime] = None
    dependientes: List[UnidadResponsableBase] = [] 

    class Config:
        orm_mode = True