from fastapi import FastAPI, HTTPException, Depends, status, Body 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import Base, engine
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager
from datetime import timedelta
from enum import Enum
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    get_admin_user,
    
)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
from .models import User, UserRoles, UserCreate, UserResponse, UnidadResponsable
from .schemas import UnidadResponsableUpdate, UnidadResponsableResponse, UnidadResponsableCreate, UnidadJerarquicaResponse, UserCreate
from .database import SessionLocal, engine, Base, get_db
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from contextlib import contextmanager
from fastapi.encoders import jsonable_encoder

USER = "USER"
ADMIN = "ADMIN"
AUDITOR = "AUDITOR"

# Context manager mejorado
@contextmanager
def session_scope():
    """Proporciona un ámbito transaccional alrededor de una serie de operaciones."""
    session = SessionLocal()  # Usamos SessionLocal en lugar de Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error de base de datos: {str(e)}"
        ) from e
    finally:
        session.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173",  # Asumiendo que tu front corre aquí
    "http://148.216.111.144",
    "http://localhost:3000", # Si tienes otro puerto o dominio para el front
    "192.168.0.124:3000",
    "*://*/*",  # Permitir todas las solicitudes de cualquier origen
    "*" # Permitir todas las solicitudes de cualquier origen
]

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["*"]
)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "SERUMICH 2.0 API is running"}

@app.get("/usuarios_contraloria", tags=["Usuario"])
def contraloria_users():
    users = []
    db_url = "postgresql://contraloria:c0ntr4l0r14@host.docker.internal:5432/contraloria"
    try:
        engine = create_engine(db_url)
        with engine.connect() as connection:
            query = text("SELECT nombre, email, username FROM public.viewmat_situm_dep_usuarios")
            result = connection.execute(query)
            users = [dict(zip(result.keys(), row)) for row in result.fetchall()]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al conectar con contraloría: {str(e)}"
        )
    return users
    
@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["Usuario"])
def register(user: UserCreate):
    with session_scope() as db:
        # ✅ Aquí el error: estaba comparando con el objeto completo
        existing_user = db.query(User).filter(User.username == user.username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )

        existing_email = db.query(User).filter(User.email == user.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso"
            )

        hashed_password = get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password,
            role= None # asignar sin valor por defecto
        )
        db.add(db_user)
        db.flush()
        return {"message": "Usuario registrado exitosamente"}

@app.post("/token", tags=["Usuario"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with session_scope() as db:
        # Verificar si el usuario existe y la contraseña es correcta
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nombre de usuario o contraseña incorrectos",
            )
        
            # comprobar si el usuario tiene un rol asignado
        if user.role is None:
            # Si el rol es None, significa que no se ha asignado un rol
            raise HTTPException(
                status_code=403,
                detail="Este usuario aun no tiene un rol asignado, Solicta acceso a un administrador"
            )
        
        # Comprobar si el isdeleted es True
        if user.is_deleted:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Usuario eliminado, no puedes iniciar sesión"
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={
                "sub": user.username,
                "user_id": user.id,
                "email": user.email,
                "username": user.username,
                "role": user.role.value if isinstance(user.role, Enum) else user.role
            },
            expires_delta=access_token_expires
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }

@app.get("/users", response_model=list[UserResponse], tags=["Usuario"])
def get_users(skip: int = 0, 
        limit: int = 1000, 
        current_user: User = Depends(get_current_user)):
    with session_scope() as db:
        users = db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
        return jsonable_encoder(users)

@app.get("/users/{user_id}", tags=["Usuario"])
def read_user(user_id: int, current_user: User = Depends(get_current_user)):
    with session_scope() as db:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return jsonable_encoder(user)

@app.delete("/users/{user_id}", tags=["Usuario"])
def soft_delete_user(user_id: int, current_user: User = Depends(get_admin_user)):
    with session_scope() as db:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        setattr(user, "is_deleted", True)
        return {"message": "Usuario marcado como eliminado"}

@app.put("/users/{user_id}/change-password", tags=["Usuario"])
def change_password(
    user_id: int,
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user),
):
    with session_scope() as db:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        if not verify_password(current_password, getattr(user, "password")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )
        
        if getattr(current_user, "id", None) != getattr(user, "id", None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No tienes permiso para realizar esta acción",
            )

        setattr(user, "password", get_password_hash(new_password))
        return {"message": "Contraseña actualizada exitosamente"}

@app.get("/me", tags=["Usuario"])
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()

# endpoint para arbol jerarquico de unidades responsables
@app.get(
    "/unidades_jerarquicas",
    response_model=List[UnidadJerarquicaResponse],
    tags=["Jerarquía de Unidades Responsables", "Unidades Responsables"]
)
def unidades_jerarquicas(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    # Asegúrate de comparar el valor real, no el objeto columna
    user_role = current_user.role.value if isinstance(current_user.role, Enum) else str(current_user.role)
    if user_role != UserRoles.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para acceder a esta información"
        )
    
    sql = text("""
        WITH RECURSIVE jerarquia AS (
            SELECT 
                u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, 0 as nivel,
                u.responsable as responsable_id
            FROM unidades_responsables u
            WHERE unidad_padre_id IS NULL
            UNION ALL
            SELECT 
                u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, j.nivel + 1,
                u.responsable as responsable_id
            FROM unidades_responsables u
            JOIN jerarquia j ON u.unidad_padre_id = j.id_unidad
        )
        SELECT 
            j.id_unidad, j.nombre, j.tipo_unidad, j.nivel, 
            us.id as responsable_id, us.username, us.email
        FROM jerarquia j
        LEFT JOIN users us ON j.responsable_id = us.id
        ORDER BY j.nivel, j.nombre;
    """)
    result = db.execute(sql).fetchall()

    unidades = []
    for row in result:
        responsable = None
        if row.responsable_id:
            responsable = {
                "id": row.responsable_id,
                "username": row.username,
                "email": row.email
            }

        unidades.append({
            "id_unidad": row.id_unidad,
            "nombre": row.nombre,
            "tipo_unidad": row.tipo_unidad,
            "nivel": row.nivel,
            "responsable": responsable
        })

    return unidades

# endpoint para crear unidades responsables
@app.post(
    "/unidades_responsables",
    response_model=UnidadResponsableResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Unidades Responsables"]
)
def create_unidades_responsables(
    unidad: UnidadResponsableCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Verificar que el usuario tiene permisos de administrador
    user_role = current_user.role.value if isinstance(current_user.role, Enum) else str(current_user.role)
    if user_role != UserRoles.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para crear unidades responsables"
        )
    #solo avisar que no tiene responsable se le asigna despues 
    if unidad.responsable is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede asignar un responsable al crear una unidad, asigna el responsable despues"
        )
    # Verificar que la unidad padre existe si se proporciona
    if unidad.unidad_padre_id:
        parent_unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad.unidad_padre_id).first()
        if not parent_unidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidad padre no encontrada"
            )
    # Verificar que el nombre de la unidad no está vacío
    if not unidad.nombre:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de la unidad es obligatorio"
        )
    # verificar que el id de unidad padre no es igual a la unidad misma
    if unidad.unidad_padre_id == unidad.id_unidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La unidad no puede ser su propia unidad padre"
        )
    # verificar que la unida id sea consecutiva al ultimo id de unidad
    last_unidad = db.query(UnidadResponsable).order_by(UnidadResponsable.id_unidad.desc()).first()
    if last_unidad and unidad.id_unidad <= last_unidad.id_unidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El ID de la unidad debe ser mayor que el último ID registrado"
        )

    # Verificar que el RFC es válido si se proporciona
    if unidad.rfc and len(unidad.rfc) != 13:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El RFC debe tener 13 caracteres"
        )
    
    # Verificar que el correo electrónico es válido si se proporciona
    if unidad.correo_electronico and "@" not in unidad.correo_electronico:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico debe ser válido"
        )
    # Verificar que el código postal es válido si se proporciona
    if unidad.codigo_postal and len(unidad.codigo_postal) != 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El código postal debe tener 5 caracteres"
        )
    # Verificar que el teléfono es válido si se proporciona
    if unidad.telefono and len(unidad.telefono) < 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El teléfono debe tener al menos 10 caracteres"
        )
    # verificar que los campos opcionales si estan vacios se avise que se llene despues
    if not unidad.domicilio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El domicilio es opcional, pero se recomienda llenarlo"
        )
    if not unidad.municipio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El municipio es opcional, pero se recomienda llenarlo"
        )
    if not unidad.localidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La localidad es opcional, pero se recomienda llenarlo"
        )
    if not unidad.tipo_unidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El tipo de unidad es opcional, pero se recomienda llenarlo"
        )
    # Crear la unidad responsable
    if unidad.responsable is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede asignar un responsable al crear una unidad, asigna el responsable despues"
        )
    if unidad.unidad_padre_id is not None and unidad.unidad_padre_id == unidad.id_unidad:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La unidad no puede ser su propia unidad padre"
        )
    if unidad.id_unidad is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede asignar un ID al crear una unidad, el ID se asigna automáticamente"
        )
# la unidd padre debe ser de las mismas unidades responsables
# hacer una consulta para seleccionar la unidad responsable
    """ if unidad.unidad_padre_id is not None:
        parent_unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad.unidad_padre_id).first()
        if not parent_unidad:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Unidad padre no encontrada"
            )
        if parent_unidad.tipo_unidad != unidad.tipo_unidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La unidad padre debe ser del mismo tipo que la unidad que se está creando"
            ) """
    try:
        # Crear la nueva unidad responsable
        new_unidad = UnidadResponsable( 
            nombre=unidad.nombre,
            telefono=unidad.telefono,
            domicilio=unidad.domicilio,
            municipio=unidad.municipio,
            localidad=unidad.localidad,
            codigo_postal=unidad.codigo_postal,
            rfc=unidad.rfc,
            correo_electronico=unidad.correo_electronico,
            responsable=unidad.responsable,  # Asignar el ID del responsable
            tipo_unidad=unidad.tipo_unidad,
            unidad_padre_id=unidad.unidad_padre_id  # Asignar el ID de la unidad padre
        )
        db.add(new_unidad)
        db.commit()
        db.refresh(new_unidad)
        return jsonable_encoder(new_unidad)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al crear la unidad responsable: {str(e)}"
        )
    
# endpoint para editar unidades responsables
@app.put(
    "/unidades_responsables/{id_unidad}",
    response_model=UnidadResponsableResponse,
    tags=["Unidades Responsables"]
)
def actualizar_unidad(
    id_unidad: int,
    unidad_actualizacion: UnidadResponsableUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Buscar la unidad existente
    db_unidad = db.query(UnidadResponsable).get(id_unidad)
    if not db_unidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró una unidad con ID {id_unidad}"
        )
    
    # Verificar si el nuevo responsable existe (si se proporciona)
    if unidad_actualizacion.responsable:
        responsable = db.query(User).get(unidad_actualizacion.responsable)
        if not responsable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un usuario con ID {unidad_actualizacion.responsable}"
            )
    
    # Verificar si la nueva unidad padre existe (si se proporciona)
    if unidad_actualizacion.unidad_padre_id:
        unidad_padre = db.query(UnidadResponsable).get(unidad_actualizacion.unidad_padre_id)
        if not unidad_padre:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró una unidad padre con ID {unidad_actualizacion.unidad_padre_id}"
            )
    
    # Actualizar los campos de la unidad
    for key, value in unidad_actualizacion.model_dump(exclude_unset=True).items():
        setattr(db_unidad, key, value)
    
    db.commit()
    db.refresh(db_unidad)
    
    return db_unidad

@app.get(
    "/unidades_responsables",
    response_model=List[UnidadResponsableResponse],
    tags=["Unidades Responsables"]
)
def read_unidades(
    skip: int = 0,
    limit: int = 1000,
    id_unidad: Optional[int] = None,
    nombre: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Construcción de la consulta base
        query = db.query(UnidadResponsable)
        
        # Aplicación de filtros
        if id_unidad:
            query = query.filter(UnidadResponsable.id_unidad == id_unidad)
        if nombre:
            query = query.filter(UnidadResponsable.nombre.ilike(f"%{nombre}%"))
        
        # Ejecución de la consulta
        unidades_db = query.offset(skip).limit(limit).all()
        
        # Manejo de resultados vacíos
        if not unidades_db:
            if id_unidad or nombre:  # Solo si hay filtros aplicados
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No se encontraron unidades con los criterios especificados"
                )
            return []  # Si no hay filtros, devolver lista vacía
        
        return jsonable_encoder(unidades_db)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al obtener unidades responsables: {str(e)}"
        )
        
@app.get(
    "/{unidad_id}",
    response_model=UnidadResponsableResponse,
    tags=["Unidades Responsables"]
)
def get_unidad(
    unidad_id: int,
    db: Session = Depends(get_db)
):
    db_unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad_id).first()
    if not db_unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    return db_unidad

@app.put(
    "/{unidad_id}/asignar-responsable",
    tags=["Unidades Responsables"]
)
def asignar_responsable(
    unidad_id: int,
    usuario_id: int,
    db: Session = Depends(get_db)
):
    # Verificar que existe la unidad
    db_unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad_id).first()
    if not db_unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")
    
    # Verificar que existe el usuario
    db_usuario = db.query(User).filter(User.id_usuario == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Asignar responsable
    db_unidad.responsable_id = usuario_id  # Usa el nombre correcto del campo FK en tu modelo
    db.commit()
    db.refresh(db_unidad)
    
    return {"message": "Responsable asignado correctamente", "unidad": db_unidad}

# endpoint para las actas_entrega_recepcion
@app.get("/actas_entrega_recepcion", tags=["Actas de Entrega Recepción"])
def actas_entrega_recepcion():
    return {"message": "Actas de Entrega Recepción"}

@app.get("/anexos", tags=["Anexos de Entrega Recepción"])
def anexos():
    return {"message": "Anexos de Entrega Recepción"}
