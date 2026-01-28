# schemas.py
from pydantic import BaseModel, ConfigDict, Field, field_validator, validator
from typing import Optional, List, Dict, Any, Union
from datetime import datetime, date, time
from sqlalchemy import Enum as PythonEnum
from enum import Enum as SQLEnum


class UserRoles(str, SQLEnum):
    USER = "USER"
    ADMIN = "ADMIN"
    AUDITOR = "AUDITOR"

# =================================================================================================
#                                           USUARIOS
# =================================================================================================

# Esquema base para usuario
class UserBase(BaseModel):
    # compatible con respnsable en unidadresponsable 
    id: Optional[int] = None
    username: Optional[str] = None
    email: Optional[str] = None
    role: Optional[UserRoles] = None
    reset_token: Optional[str] = None
    reset_token_expiration: Optional[datetime] = None



# Esquema para creación de usuario (incluye password)
class UserCreate(UserBase):
    username: str
    email: str
    password: str

class UserDB(UserBase):
    id: int
    is_deleted: bool = False
    hashed_password: str

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_deleted": self.is_deleted
        }

class ForgotPasswordRequest(BaseModel):
    email: str

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    
    @validator('new_password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        return v

class UnidadResponsableSimple(BaseModel):
    id_unidad: int
    nombre: str

    class Config:
        orm_mode = True

# Esquema para respuesta (sin password)
class UserResponse(UserBase):
    id: int
    username: str
    email: str
    role: Optional[str] = None  # Ahora es opcional sin valor por defecto
    is_deleted: bool
    reset_token: Optional[str] = None
    reset_token_expiration: Optional[datetime] = None
    # incluir la unidad responsable si existe
    unidad_responsable: Optional[UnidadResponsableSimple] = None

    __allow_unmapped_fields__ = True

    class Config:
        orm_mode = True

# Esquema para actualización (todos los campos opcionales)
class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[UserRoles] = None
    

# =================================================================================================
#                                     UNIDADES RESPONSABLES
# =================================================================================================

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
    # el responsabl edebe ser compatibel con usuario 
    responsable: Optional[UserBase] = None  # Asegúrate que UserBase esté bien definido 
    tipo_unidad: Optional[str] = None
    unidad_padre_id: Optional[int] = None  # ID de la unidad responsable padre

    @field_validator('responsable', mode='before')
    def tranform_responsable(cls, v):
        # si el valor es un ID numerico, se convierte a None
        return None if isinstance(v, int) else v
    class Config:
        orm_mode = True

# Esquema para creación de Unidad Responsable
class UnidadResponsableCreate(UnidadResponsableBase):
    pass

# Esquema para actualización de Unidad Responsable
class UnidadResponsableUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    domicilio: Optional[str] = None
    municipio: Optional[str] = None
    localidad: Optional[str] = None
    codigo_postal: Optional[str] = None
    rfc: Optional[str] = None
    correo_electronico: Optional[str] = None
    responsable: Optional[UserBase] = None
    tipo_unidad: Optional[str] = None
    unidad_padre_id: Optional[int] = None
    responsable_id: Optional[int] = None
    class Config:
        orm_mode = True

# Esquema para respuesta de Unidad Responsable
# (AnexoResponse movido a la sección de ANEXOS)

class UnidadResponsableResponse(BaseModel):
    id_unidad: int
    nombre: str
    telefono: Optional[str] = None
    domicilio: Optional[str] = None
    municipio: Optional[str] = None
    localidad: Optional[str] = None
    codigo_postal: Optional[str] = None
    rfc: Optional[str] = None
    correo_electronico: Optional[str] = None
    tipo_unidad: Optional[str] = None
    fecha_creacion: Optional[datetime] = None
    fecha_cambio: Optional[datetime] = None
    responsable: Optional[UserBase] = None  # Asegúrate que UserBase esté bien definido
    dependientes: List[UnidadResponsableBase] = Field(default_factory=list)  # Usa Field para listas
    
    class Config:
        orm_mode = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

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

# =================================================================================================
#                                           ANEXOS
# =================================================================================================

################### Anexo 
class AnexoBase(BaseModel):
    id: Optional[int] = None
    clave: str
    creador_id: int
    datos: List[Dict[str, Any]]
    estado: Optional[str] = None
    unidad_responsable_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None
    acta_id: Optional[int] = None   

class AnexoCreate(AnexoBase):
    clave: str
    creador_id: int
    datos: List[Dict[str, Any]]
    estado: str = "Borrador"
    unidad_responsable_id: int

class AnexoUpdate(AnexoBase):
    clave: Optional[str] = None
    creador_id: Optional[int] = None
    datos: Optional[List[Dict[str, Any]]] = None
    estado: Optional[str] = None
    unidad_responsable_id: Optional[int] = None
    fecha_creacion: Optional[datetime] = None

class AnexoResponse(AnexoBase):
    id:int 
    creado_en: date
    actualizado_en: date

    class Config:
        from_attributes = True
        json_encoders= {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
        }

# =================================================================================================
#                                ACTAS DE ENTREGA-RECEPCIÓN
# =================================================================================================

# schema para acta entrega recepcion
# esquema para crear un anexo###################################################################################

# Schema para crear actas (POST)
# Schema base para Acta (sin relaciones)
class ActaCreate(BaseModel):
    unidad_responsable: int = Field(..., description="ID de la unidad responsable")
    folio: str = Field(..., description="Número de folio del acta")
    fecha: str = Field(..., description="Fecha del acta (YYYY-MM-DD)")
    hora: Optional[str] = Field(None, description="Hora del acta (HH:MM)")
    comisionado: str = Field(..., description="Nombre del comisionado")
    oficio_comision: Optional[str] = Field(None, description="Número de oficio de comisión")
    fecha_oficio_comision: Optional[str] = Field(None, description="Fecha del oficio de comisión")
    entrante: Optional[str] = Field(None, description="Nombre de la persona entrante")
    ine_entrante: Optional[str] = Field(None, description="INE de la persona entrante")
    fecha_inicio_labores: Optional[str] = Field(None, description="Fecha de inicio de labores")
    nombramiento: Optional[str] = Field(None, description="Tipo de nombramiento")
    fecha_nombramiento: Optional[str] = Field(None, description="Fecha del nombramiento")
    asignacion: Optional[str] = Field(None, description="Tipo de asignación")
    asignado_por: Optional[str] = Field(None, description="Quién realiza la asignación")
    domicilio_entrante: Optional[str] = Field(None, description="Domicilio de la persona entrante")
    telefono_entrante: Optional[str] = Field(None, description="Teléfono de la persona entrante")
    saliente: Optional[str] = Field(None, description="Nombre de la persona saliente")
    fecha_fin_labores: Optional[str] = Field(None, description="Fecha de fin de labores")
    testigo_entrante: Optional[str] = Field(None, description="Nombre del testigo entrante")
    ine_testigo_entrante: Optional[str] = Field(None, description="INE del testigo entrante")
    testigo_saliente: Optional[str] = Field(None, description="Nombre del testigo saliente")
    ine_testigo_saliente: Optional[str] = Field(None, description="INE del testigo saliente")
    fecha_cierre_acta: Optional[str] = Field(None, description="Fecha de cierre del acta")
    hora_cierre_acta: Optional[str] = Field(None, description="Hora de cierre del acta")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    estado: Optional[str] = Field("Pendiente", description="Estado del acta")

# Schema para respuesta básica de Acta
class ActaResponse(BaseModel):
    id: int
    unidad_responsable: int
    folio: str
    fecha: str
    hora: Optional[str]
    comisionado: str
    oficio_comision: Optional[str]
    fecha_oficio_comision: Optional[str]
    entrante: Optional[str]
    ine_entrante: Optional[str]
    fecha_inicio_labores: Optional[str]
    nombramiento: Optional[str]
    fecha_nombramiento: Optional[str]
    asignacion: Optional[str]
    asignado_por: Optional[str]
    domicilio_entrante: Optional[str]
    telefono_entrante: Optional[str]
    saliente: Optional[str]
    fecha_fin_labores: Optional[str]
    testigo_entrante: Optional[str]
    ine_testigo_entrante: Optional[str]
    testigo_saliente: Optional[str]
    ine_testigo_saliente: Optional[str]
    fecha_cierre_acta: Optional[str]
    hora_cierre_acta: Optional[str]
    observaciones: Optional[str]
    estado: Optional[str]
    # Hacer estos campos opcionales temporalmente
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
    anexos: Optional[List[AnexoResponse]] = None  # ← Anexos relacionados

    class Config:
        from_attributes = True

# Schema para respuesta con datos de unidad
class ActaWithUnidadResponse(ActaResponse):
    unidad_nombre: Optional[str] = None
    unidad_descripcion: Optional[str] = None

    class Config:
        from_attributes = True

class ActaUpdate(BaseModel):
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
    # Hacer estos campos opcionales temporalmente
    creado_en: Optional[datetime] = None
    actualizado_en: Optional[datetime] = None
   


