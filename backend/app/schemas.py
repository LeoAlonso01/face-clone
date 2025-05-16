# schemas.py
from pydantic import BaseModel
from typing import Optional
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