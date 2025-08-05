# schemas.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date, time
from sqlalchemy import Enum
from enum import Enum


class UserRoles(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"

# Esquema base para usuario
class UserBase(BaseModel):
    username: str
    email: str
    # role optional sin valor por defecto
    role: Optional[UserRoles] = None
    """ unidad_responsable_id: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None """

# Esquema para creación de usuario (incluye password)
class UserCreate(UserBase):
    username: str
    email: str
    password: str
    role: Optional[UserRoles] = None  # Ahora es opcional sin valor por defecto

# Esquema para respuesta (sin password)
class UserResponse(UserBase):
    id: int
    username: str
    email: str
    role: Optional[UserRoles] = None  # Ahora es opcional sin valor por defecto
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
    """ nombre: Optional[str] = None
    unidad_responsable_id: Optional[str] = None
    domicilio: Optional[str] = None
    telefono: Optional[str] = None """

# Esquema para Unidad Responsable
# Es una unidad responsable en el sistema, como un departamento u oficina.
class UnidadResponsableBase(BaseModel):
    id_unidad: Optional[int] = None
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

class ResponsableResumen(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        orm_mode = True

class UnidadJerarquicaResponse(BaseModel):
    id_unidad: int
    nombre: str
    tipo_unidad: Optional[str]
    nivel: int
    responsable: Optional[ResponsableResumen]

    class Config:
        orm_mode = True

class ActaEntregaRecepcionBase(BaseModel):
    # campos con valores por defecto
    id: Optional[int] = None
    creado_en: Optional[str] = None
    actualizado_en: Optional[str] = None


    unidad_responsable: Optional[int] = None
    folio: Optional[str] = None
    fecha: Optional[str] = None
    hora: Optional[str] = None
    comisionado: Optional[str] = None
    oficio_comision: Optional[str] = None
    fecha_oficio_comision: Optional[str] = None
    entrante: Optional[str] = None
    ine_entrante: Optional[str] = None
    fecha_inicio_labores: Optional[str] = None
    nombramiento: Optional[str] = None
    fecha_nombramiento: Optional[str] = None
    asignacion: Optional[str] = None
    asignado_por: Optional[str] = None
    domicilio_entrante: Optional[str] = None
    telefono_entrante: Optional[str] = None
    saliente: Optional[str] = None
    fecha_fin_labores: Optional[str] = None
    testigo_entrante: Optional[str] = None
    ine_testigo_entrante: Optional[str] = None
    testigo_saliente: Optional[str] = None
    ine_testigo_saliente: Optional[str] = None
    fecha_cierre_acta: Optional[str] = None
    hora_cierre_acta: Optional[str] = None
    observaciones: Optional[str] = None
    estado: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            time: lambda v: v.isoformat() if v else None
        }
   

class ActaEntregaRecepcionCreate(ActaEntregaRecepcionBase):
    pass

class ActaEntregaRecepcion(ActaEntregaRecepcionBase):
    id: int
    creado_en: datetime
    actualizado_en: datetime

    class Config:
        orm_mode = True

# Esquema para Anexo
class AnexoBase(BaseModel):
    id: int
    clave_id: int | None
    creador_id: int | None
    fecha_creacion: datetime | None
    datos: str | None
    estado: str | None
    unidad_responsable_id: int | None
    creado_en: datetime
    actualizado_en: datetime
    is_deleted: bool = False  # Soft delete

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }

class AnexoCreate(AnexoBase):
    pass
class AnexoResponse(AnexoBase):

    id: int
    fecha_creacion: datetime
    creado_en: date
    actualizado_en: date
    unidad_responsable_id: int
    estado: str

    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }

class AnexoUpdate(AnexoBase):
    clave_id: Optional[int] = None
    creador_id: Optional[int] = None
    datos: Optional[dict] = None
    estado: Optional[str] = None
    unidad_responsable_id: Optional[int] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None
        }
        orm_mode = True
        
