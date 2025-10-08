import secrets
import string
from fastapi import BackgroundTasks, FastAPI, HTTPException, Depends, status, Body, Query 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import Base, engine
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager
from datetime import date, timedelta, datetime
from enum import Enum
import logging
from .auth import (
    authenticate_user,
    create_access_token,
    enviar_email_recuperacion,
    get_current_user,
    get_password_hash,
    verify_password,
    get_admin_user,
    
)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
from .models import Anexos, User, UserRoles, UnidadResponsable
from .schemas import ActaResponse, ActaCreate, ActaUpdate, ForgotPasswordRequest, UserResponse, AnexoUpdate
from .models import ActaEntregaRecepcion
from .schemas import AnexoCreate, AnexoResponse
from .schemas import UnidadResponsableUpdate, UnidadResponsableResponse, UnidadResponsableCreate, UnidadJerarquicaResponse, UserCreate
from .database import SessionLocal, engine, Base, get_db
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy.sql import text
from contextlib import contextmanager
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload
from fastapi import UploadFile, File
import os
from fastapi.staticfiles import StaticFiles


UPLOAD_DIR = "/app/uploads/pdfs"
STATIC_DIR = "/app/static/pdfs"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

async def save_pdf(file: UploadFile):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten PDFs")

    filename = file.filename
    upload_path = os.path.join(UPLOAD_DIR, filename)
    static_path = os.path.join(STATIC_DIR, filename)

    # Guardar en uploads
    with open(upload_path, "wb") as f:
        f.write(await file.read())

    # Copiar a static para servirlo
    import shutil
    shutil.copy(upload_path, static_path)

    # URL pública
    file_url = f"http://localhost:8000/static/pdfs/{filename}"
    return {"file_url": file_url}

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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
<<<<<<< HEAD
    "http://148.216.111.144",
    "http://localhost:3000", # Si tienes otro puerto o dominio para el front
    "192.168.0.124:3000",
=======
>>>>>>> 6c6851e69f7d891e22c90dc30bf8c50e7517fbbd
    "http://localhost:3000", # Si tienes otro puerto o dominio para el front
    "https://entrega-recepcion-frontend-82zrt1b9a.vercel.app/",
    "https://entrega-recepcion-git-91bd1d-utm221001tim-ut-moreliaes-projects.vercel.app/"
]

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://(localhost|127\.0\.0\.1)(:\d+)?",  # Localhost con cualquier puerto
    allow_origins=["*"],  # Permite todos los orígenes TEMPORALMENTE
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# generacion token seguro
def generar_token_seguro(length: int = 32 ) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "SERUMICH 2.0 API is running"}

@app.post("/pdf", tags=["Archivos"])
async def upload_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")

    # Generar nombre único
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    static_path = os.path.join(STATIC_DIR, filename)

    # Guardar en uploads
    content = await file.read()
    with open(file_path, "wb") as buffer:
        buffer.write(content)

    # Copiar a static para servirlo públicamente
    with open(static_path, "wb") as buffer:
        buffer.write(content)

    # URL pública
    file_url = f"http://localhost:8000/static/pdfs/{filename}"

    return {"url": file_url}

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
            created_at=datetime.now(),
            updated_at=datetime.now(),
            is_deleted=False,
            role= None # asignar sin valor por defecto
        )
        db.add(db_user)
        db.flush()

        return {
            "message": "Usuario registrado exitosamente",
            "user:" : {
                "id": db_user.id,
                "username": db_user.username,
                "email": db_user.email,
                "role": db_user.role.value if isinstance(db_user.role, Enum) else db_user.role
            }
        }

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
        
        # obtener la unidad responsable del usuario
        
        
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
        #current_user: User = Depends(get_current_user)
        ):
    with session_scope() as db:
        users = db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
        return jsonable_encoder(users)

@app.get("/users/{user_id}", tags=["Usuario"])
def read_user(
    user_id: int, 
    # current_user: User = Depends(get_current_user)
    ):
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
    # current_user: User = Depends(get_current_user),
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

        setattr(user, "password", get_password_hash(new_password))
        return {"message": "Contraseña actualizada exitosamente"}

@app.post("/forgot-password", tags=["Usuario"])
async def forgot_password(
    request: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    # buscar usuario por email
     # Buscar usuario por email
    user = db.query(User).filter(User.email == request.email, User.is_deleted == False).first()

    # Si no existe, no revelamos información (seguridad)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Si el email está registrado, recibirás instrucciones para recuperar tu contraseña."
        )

    # Generar token y expiración (15 minutos)
    token = generar_token_seguro()
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    # Guardar en la base de datos
    user.reset_token = token
    user.reset_expires = expires_at
    db.commit()

    # Enviar correo en segundo plano (mañana lo activamos)
    try:
        background_tasks.add_task(
            enviar_email_recuperacion,
            destinatario=user.email,
            nombre_usuario=user.username,
            token=token
        )
    except Exception as e:
        print(f"[WARN] No se pudo programar el envío de correo: {e}")
        # No detenemos el flujo

    return {
        "message": "Si el email está registrado, recibirás instrucciones para recuperar tu contraseña."
    }
    

# Agrega este endpoint temporal para diagnóstico
@app.get("/debug/unidad-estructura")
async def debug_unidad_estructura(db: Session = Depends(get_db)):
    unidad_ejemplo = db.query(UnidadResponsable).first()
    if not unidad_ejemplo:
        return {"error": "No hay unidades en la base de datos"}
    
    return {
        "columnas": unidad_ejemplo.__dict__,
        "relaciones": [rel for rel in dir(unidad_ejemplo) if not rel.startswith('_')]
    }

# endpont para obtener unidad por usuario
@app.get("/unidad_por_usuario/{user_id}")
def obtener_unidad_por_usuario(user_id:int, db: Session = Depends(get_db)):
    usuario = db.query(User).filter(User.id == user_id).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    if not usuario.unidad:
        raise HTTPException(status_code=404, detail="El usuario no tiene una unidad responsable asignada")

    unidad = usuario.unidad

    return {
        "id_unidad": unidad.id_unidad,
        "nombre": unidad.nombre,
        "responsable": {
            "id": unidad.usuario_responsable.id,
            "nombre": unidad.usuario_responsable.username
        }
    }

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

""" @app.get(
    "/unidades_responsables",
    response_model=List[UnidadResponsableResponse],
    tags=["Unidades Responsables"]
)
def read_unidades(
    skip: int = 0,
    limit: int = 1000,
    id_unidad: Optional[int] = None,
    nombre: Optional[str] = None,
    # current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Asegurarnos de que la relación se llama correctamente
        query = db.query(UnidadResponsable).options(
            joinedload(UnidadResponsable.usuario_responsable)  # Carga la relación
        )

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
        ) """



@app.get("/unidades_responsables", 
         response_model=List[UnidadResponsableResponse],
         tags=["Unidades Responsables"])
def read_unidades(db: Session = Depends(get_db)):
    try:
        # Carga la unidad + usuario_responsable + anexos
        query = db.query(UnidadResponsable).options(
            joinedload(UnidadResponsable.usuario_responsable)
        )
        
        unidades = query.all()
        
        # Transformamos los resultados
        for unidad in unidades:
            if unidad.usuario_responsable:
                unidad.responsable = UserResponse(
                    id=unidad.usuario_responsable.id,
                    username=unidad.usuario_responsable.username,
                    email=unidad.usuario_responsable.email,
                    role=unidad.usuario_responsable.role,
                    is_deleted=unidad.usuario_responsable.is_deleted
                )
            else:
                unidad.responsable = None
        
        return unidades
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener unidades: {str(e)}"
        )

@app.get(
    "/unidades_responsables/{unidad_id}",
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
    "/unidades_responsables/{unidad_id}/asignar-responsable",
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
    db_usuario = db.query(User).filter(User.id_usuario == usuario_id, User.is_deleted == False).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Asignar responsable
    db_unidad.responsable = db_usuario  # Usa el nombre correcto del campo FK en tu modelo
    db.commit()
    db.refresh(db_unidad)
    
    return {"message": "Responsable asignado correctamente", "unidad": db_unidad}




# endpoints para las actas entregarecepcion

@app.get("/actas", response_model=List[ActaResponse], tags=["Actas de Entrega Recepción"])
def read_actas(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    try:
        actas = (
            db.query(ActaEntregaRecepcion)
            .options(
                selectinload(ActaEntregaRecepcion.unidad)
                .selectinload(UnidadResponsable.anexos)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not actas:
            return []
        return actas
    except Exception as e:
        print(f"Error detallado en /actas: {type(e).__name__}: {e}")  # Log clave
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/actas/{acta_id}", response_model=ActaResponse, tags=["Actas de Entrega Recepción"])
def read_acta(acta_id: int, db: Session = Depends(get_db)):
    db_acta = db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.id == acta_id).first()
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    return db_acta

@app.post("/actas", response_model=ActaResponse, status_code=status.HTTP_201_CREATED)
def crear_acta(acta: ActaCreate, db: Session = Depends(get_db)):
    """
    Crear una nueva acta de entrega-recepción
    """
    try:
        # Validar que la unidad responsable existe
        unidad = db.query(UnidadResponsable).filter(
            UnidadResponsable.id_unidad == acta.unidad_responsable
        ).first()
        
        if not unidad:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unidad responsable con ID {acta.unidad_responsable} no existe"
            )
        
        # Verificar si ya existe un folio
        existing_acta = db.query(ActaEntregaRecepcion).filter(
            ActaEntregaRecepcion.folio == acta.folio
        ).first()
        
        if existing_acta:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un acta con el folio {acta.folio}"
            )
        
        # Crear nueva acta
        db_acta = ActaEntregaRecepcion(**acta.model_dump(exclude_unset=True))
        db.add(db_acta)
        db.commit()
        db.refresh(db_acta)
        
        # Si los campos de fecha son None, asignar valores por defecto
        if db_acta.creado_en is None:
            db_acta.creado_en = datetime.utcnow()
        if db_acta.actualizado_en is None:
            db_acta.actualizado_en = datetime.utcnow()
            
        db.commit()
        db.refresh(db_acta)
        
        return db_acta
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear acta: {str(e)}")

@app.put("/actas/{acta_id}", response_model=ActaResponse, tags=["Actas de Entrega Recepción"])
def update_acta(acta_id: int, acta: ActaUpdate, db: Session = Depends(get_db)):
    db_acta = db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.id == acta_id).first()
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    for key, value in acta.dict(exclude_unset=True).items():
        setattr(db_acta, key, value)
    db.commit()
    db.refresh(db_acta)
    return db_acta


@app.delete("/actas/{acta_id}", tags=["Actas de Entrega Recepción"])
def delete_acta(acta_id: int, db: Session = Depends(get_db)):
    db_acta = db.query(ActaEntregaRecepcion).filter(
        ActaEntregaRecepcion.id == acta_id
    ).first()
    
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    # Opción 1: Eliminación real
    db.delete(db_acta)
    db.commit()
    return {"message": "Acta eliminada correctamente"}

# actas con anexos por unidad responsable y por creador 


# endpoints para anexos #############################################################################################
@app.get("/anexos", response_model=List[AnexoResponse], tags=["Anexos de Entrega Recepción"])
def read_anexos(
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db)
):
    try:
        anexos = db.query(Anexos).filter(Anexos.is_deleted == False).offset(skip).limit(limit).all()
        if not anexos:
            return []
        return anexos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar la base de datos: {str(e)}")
    
# add by POST
@app.post("/anexos", response_model=AnexoResponse, tags=["Anexos de Entrega Recepción"])
def create_anexo(anexo: AnexoCreate, db: Session = Depends(get_db)):
    
    db_anexo = Anexos(clave=anexo.clave,
        creador_id=anexo.creador_id,
        datos=anexo.datos,
        estado=anexo.estado,
        unidad_responsable_id=anexo.unidad_responsable_id,
        fecha_creacion=anexo.fecha_creacion or datetime.utcnow(),
        creado_en=date.today(),
        actualizado_en=date.today(),
        is_deleted=False)
    
    db.add(db_anexo)
    db.commit()
    db.refresh(db_anexo)
    return db_anexo
    
# get by id
@app.get("/anexos/{anexo_id}", response_model=AnexoResponse, tags=["Anexos de Entrega Recepción"])
def read_anexo(anexo_id: int, db: Session = Depends(get_db)):
    db_anexo = db.query(Anexos).filter(Anexos.id == anexo_id, Anexos.is_deleted == False).first()
    if not db_anexo:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")
    return db_anexo



# upload pdf 
