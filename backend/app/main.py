import secrets
import string
from fastapi import BackgroundTasks, FastAPI, HTTPException, Depends, status, Body, Query, Request 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import Base, engine
from typing import List
from fastapi.middleware.cors import CORSMiddleware
from .middleware import AuditMiddleware
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
from .audit import create_audit_log
ACCESS_TOKEN_EXPIRE_MINUTES = 30
from .models import Anexos, User, UserRoles, UnidadResponsable, PasswordAuditLog, AuditLog, Cargo, UserCargoHistorial
from .schemas import ActaResponse, ActaCreate, ActaUpdate, ForgotPasswordRequest, ChangePasswordRequest, UserResponse, AnexoUpdate, ResetPasswordRequest, PasswordChangeResponse
from .models import ActaEntregaRecepcion
from .schemas import AnexoCreate, AnexoResponse, CargoCreate, CargoResponse, UserCargoHistorialCreate, UserCargoHistorialResponse
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
    "https://entrega-recepcion-frontend.vercel.app",
    "https://entrega-recepcion.umich.mx",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # <-- NO "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para capturar IP y user-agent (disponible en request.state.client_ip)
app.add_middleware(AuditMiddleware)

# generacion token seguro
def generar_token_seguro(length: int = 32 ) -> str:
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# =================================================================================================
#                                           ROOT
# =================================================================================================
@app.get("/", tags=["Root"])
def read_root():
    return {"message": "SERUMICH 2.0 API is running"}

# =================================================================================================
#                                           ARCHIVOS
# =================================================================================================
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

# =================================================================================================
#                                           USUARIOS
# =================================================================================================
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
        db: Session = Depends(get_db), 
        #current_user: User = Depends(get_current_user)
        ):
    users = (
        db.query(User)
        .filter(User.is_deleted == False)
        .offset(skip)
        .limit(limit)
        .all()
    )
    # forzar normalizacion hacia el schema UserResponse (evitar problemas de serialización con objetos SQLAlchemy)
    return [UserResponse.model_validate(u) for u in users]

@app.get("/users/{user_id}", response_model=UserResponse, tags=["Usuario"])
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = (
        db.query(User)
        .options(
            joinedload(User.unidad),
            selectinload(User.cargos_historial).joinedload(UserCargoHistorial.cargo),
        )
        .filter(User.id == user_id, User.is_deleted == False)
        .first()
    )

    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cargos_act = [
        h for h in (user.cargos_historial or [])
        if (h.fecha_fin is None and not h.is_deleted)
    ]
    user.cargos_actuales = cargos_act

    return user



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

@app.post("/users/{user_id}/change_password", response_model=PasswordChangeResponse, tags=["Usuario"])
def change_password(
    user_id: int,
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    request: Request = None
):
    """
    Permite a un usuario cambiar su propia contraseña o a un admin cambiar la de cualquier usuario.
    
    - **user_id**: ID del usuario cuya contraseña se va a cambiar
    - **current_password**: Contraseña actual del usuario (requerida para validación)
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)
    
    Seguridad:
    - Los usuarios solo pueden cambiar su propia contraseña
    - Los admins pueden cambiar la contraseña de cualquier usuario
    - Se valida que la contraseña actual sea correcta
    - La nueva contraseña debe cumplir con políticas mínimas
    """
    # Validar permisos: el usuario solo puede cambiar su propia contraseña, a menos que sea admin
    if current_user.id != user_id and current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para cambiar la contraseña de otro usuario",
        )
    
    with session_scope() as db:
        # Buscar el usuario objetivo
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )

        # Validar que la contraseña actual sea correcta
        if not verify_password(password_data.current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )

        # Validar que la nueva contraseña sea diferente a la actual
        if verify_password(password_data.new_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña no puede ser igual a la actual",
            )

        # Hash de la nueva contraseña con bcrypt (cost 12 por defecto en passlib)
        user.password = get_password_hash(password_data.new_password)
        user.updated_at = datetime.utcnow()
        
        # Registrar auditoría si un admin cambió la contraseña de otro usuario
        if current_user.id != user_id:
            audit_log = PasswordAuditLog(
                admin_id=current_user.id,
                target_user_id=user_id,
                action="password_change",
                success=True
            )
            db.add(audit_log)

        # Registro genérico en audit_logs
        try:
            create_audit_log(
                db=db,
                actor_id=current_user.id,
                action='change_password',
                object_type='user',
                object_id=user_id,
                metadata={"admin_override": current_user.id != user_id},
                ip=(request.state.client_ip if request else None)
            )
        except Exception:
            pass
        
        db.commit()
        
        logger.info(f"Contraseña cambiada exitosamente para usuario {user_id} por usuario {current_user.id}")
        
        return PasswordChangeResponse(
            message="Contraseña actualizada exitosamente",
            success=True
        )

@app.post("/admin/users/{user_id}/reset_password", response_model=PasswordChangeResponse, tags=["Usuario", "Admin"])
def reset_password(
    user_id: int,
    password_data: ResetPasswordRequest,
    current_user: User = Depends(get_admin_user),
    request: Request = None,
):
    """
    Permite a un administrador resetear la contraseña de cualquier usuario.
    
    - **user_id**: ID del usuario cuya contraseña se va a resetear
    - **new_password**: Nueva contraseña (mínimo 8 caracteres)
    
    Seguridad:
    - Solo los administradores pueden usar este endpoint
    - Se registra un log de auditoría con admin_id, target_user_id y timestamp
    - La contraseña se hashea con bcrypt (cost 12)
    - NO se devuelve la contraseña en la respuesta
    
    Recomendación: Forzar cambio de contraseña en el próximo login
    """
    with session_scope() as db:
        # Buscar el usuario objetivo
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        
        # Hash de la nueva contraseña con bcrypt
        user.password = get_password_hash(password_data.new_password)
        user.updated_at = datetime.utcnow()
        
        # Registrar auditoría (OBLIGATORIO para seguridad)
        audit_log = PasswordAuditLog(
            admin_id=current_user.id,
            target_user_id=user_id,
            action="password_reset",
            success=True
        )
        db.add(audit_log)

        # Registro genérico en audit_logs
        try:
            create_audit_log(
                db=db,
                actor_id=current_user.id,
                action='reset_password',
                object_type='user',
                object_id=user_id,
                metadata={"note": "admin_reset"},
                ip=(request.state.client_ip if request else None)
            )
        except Exception:
            pass
        
        db.commit()
        
        # Log en el sistema (NO incluir contraseña)
        logger.info(
            f"[AUDIT] Admin {current_user.id} ({current_user.username}) "
            f"reseteó la contraseña del usuario {user_id} ({user.username}) "
            f"en {datetime.utcnow().isoformat()}"
        )
        
        return PasswordChangeResponse(
            message=f"Contraseña reseteada exitosamente para el usuario {user.username}",
            success=True
        )

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

# =================================================================================================
#                                           DEBUG
# =================================================================================================
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

# =================================================================================================
#                                   UNIDADES RESPONSABLES
# =================================================================================================
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
    if unidad_actualizacion.responsable_id is not None:
        responsable = db.query(User).get(unidad_actualizacion.responsable_id)
        if not responsable:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No se encontró un usuario con ID {unidad_actualizacion.responsable_id}"
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
    data = unidad_actualizacion.model_dump(exclude_unset=True)
    if "responsable_id" in data:
        db_unidad.responsable = data.pop("responsable_id")
    # Soporte para objeto 'responsable' anidado { "responsable": { "id": 1 } }
    if "responsable" in data:
        resp = data.pop("responsable")
        if resp is None:
            db_unidad.responsable = None
        else:
            resp_id = None
            try:
                resp_id = getattr(resp, "id", None)
            except Exception:
                pass
            if resp_id is None and isinstance(resp, dict):
                resp_id = resp.get("id")
            if resp_id is None:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="El objeto 'responsable' debe incluir el campo 'id'"
                )
            responsable = db.query(User).get(resp_id)
            if not responsable:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No se encontró un usuario con ID {resp_id}"
                )
            db_unidad.responsable = resp_id
    for key, value in data.items():
        setattr(db_unidad, key, value)
    
    db.commit()
    db.refresh(db_unidad)
    
    # Preparar respuesta con responsable embebido
    if db_unidad.usuario_responsable:
        db_unidad.responsable = UserResponse(
            id=db_unidad.usuario_responsable.id,
            username=db_unidad.usuario_responsable.username,
            email=db_unidad.usuario_responsable.email,
            role=db_unidad.usuario_responsable.role,
            is_deleted=db_unidad.usuario_responsable.is_deleted,
        )
    else:
        db_unidad.responsable = None
    
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


# =================================================================================================
#                                           CARGOS
# =================================================================================================
@app.get("/cargos", response_model=List[CargoResponse], tags=["Cargos"])
def read_cargos(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    cargos = db.query(Cargo).filter(Cargo.is_deleted == False).offset(skip).limit(limit).all()
    return cargos


@app.get("/cargos/{cargo_id}", response_model=CargoResponse, tags=["Cargos"])
def get_cargo(cargo_id: int, db: Session = Depends(get_db)):
    c = db.query(Cargo).filter(Cargo.id == cargo_id, Cargo.is_deleted == False).first()
    if not c:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    return c


@app.post("/cargos", response_model=CargoResponse, tags=["Cargos"])
def create_cargo(cargo: CargoCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    # Verificar unicidad
    existing = db.query(Cargo).filter(Cargo.nombre == cargo.nombre, Cargo.is_deleted == False).first()
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un cargo con ese nombre")
    db_obj = Cargo(**cargo.model_dump(exclude_unset=True))
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    try:
        create_audit_log(db=db, actor_id=current_admin.id, action='create_cargo', object_type='cargo', object_id=db_obj.id, metadata={'nombre': db_obj.nombre})
    except Exception:
        pass
    return db_obj


@app.put("/cargos/{cargo_id}", response_model=CargoResponse, tags=["Cargos"])
def update_cargo(cargo_id: int, cargo: CargoCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    db_obj = db.query(Cargo).filter(Cargo.id == cargo_id, Cargo.is_deleted == False).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    changes = cargo.model_dump(exclude_unset=True)
    for k, v in changes.items():
        setattr(db_obj, k, v)
    db.commit()
    db.refresh(db_obj)
    try:
        create_audit_log(db=db, actor_id=current_admin.id, action='update_cargo', object_type='cargo', object_id=db_obj.id, metadata={'changes': changes})
    except Exception:
        pass
    return db_obj


@app.delete("/cargos/{cargo_id}", tags=["Cargos"])
def delete_cargo(cargo_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    db_obj = db.query(Cargo).filter(Cargo.id == cargo_id, Cargo.is_deleted == False).first()
    if not db_obj:
        raise HTTPException(status_code=404, detail="Cargo no encontrado")
    db_obj.is_deleted = True
    db.commit()
    try:
        create_audit_log(db=db, actor_id=current_admin.id, action='delete_cargo', object_type='cargo', object_id=cargo_id)
    except Exception:
        pass
    return {"message": "Cargo eliminado (soft-delete)"}


# =================================================================================================
#                               HISTORIAL DE CARGOS (user_cargo_historial)
# =================================================================================================
@app.get("/user_cargo_historial", response_model=List[UserCargoHistorialResponse], tags=["Cargos"])
def read_user_cargo_historial(
    user_id: int | None = None,
    cargo_id: int | None = None,
    unidad_responsable_id: int | None = None,
    skip: int = 0,
    limit: int = 1000,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Permisos: admin puede ver todo; usuario normal solo su propio historial
    if current_user.role != UserRoles.ADMIN and user_id and user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este historial")

    q = db.query(UserCargoHistorial).filter(UserCargoHistorial.is_deleted == False)
    if user_id:
        q = q.filter(UserCargoHistorial.user_id == user_id)
    if cargo_id:
        q = q.filter(UserCargoHistorial.cargo_id == cargo_id)
    if unidad_responsable_id:
        q = q.filter(UserCargoHistorial.unidad_responsable_id == unidad_responsable_id)

    items = q.offset(skip).limit(limit).all()
    return items


@app.get("/user_cargo_historial/{hist_id}", response_model=UserCargoHistorialResponse, tags=["Cargos"])
def get_user_cargo_historial(hist_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    entry = db.query(UserCargoHistorial).filter(UserCargoHistorial.id == hist_id, UserCargoHistorial.is_deleted == False).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    if current_user.role != UserRoles.ADMIN and entry.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="No tienes permiso para ver este registro")
    return entry


@app.post("/user_cargo_historial", response_model=UserCargoHistorialResponse, tags=["Cargos"])
def create_user_cargo_historial(payload: UserCargoHistorialCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    # Validaciones FK (pre-checks)
    cargo = db.query(Cargo).filter(Cargo.id == payload.cargo_id, Cargo.is_deleted == False).first()
    if not cargo:
        raise HTTPException(status_code=400, detail="Cargo no existente")
    user = db.query(User).filter(User.id == payload.user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=400, detail="Usuario no existente")
    unidad = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == payload.unidad_responsable_id).first()
    if not unidad:
        raise HTTPException(status_code=400, detail="Unidad responsable no existente")

    from sqlalchemy.exc import IntegrityError
    from sqlalchemy import select

    # Transacción con bloqueo para evitar condiciones de carrera
    try:
        # bloquear fila de cargo y de unidad para sincronizar concurrentes
        db.execute(select(Cargo).where(Cargo.id == payload.cargo_id).with_for_update(of=Cargo))
        # lock only the `unidades_responsables` table — avoid FOR UPDATE on outer joins
        db.execute(select(UnidadResponsable).where(UnidadResponsable.id_unidad == payload.unidad_responsable_id).with_for_update(of=UnidadResponsable))

        # comprobar asignación activa
        active = db.query(UserCargoHistorial).filter(
            UserCargoHistorial.cargo_id == payload.cargo_id,
            UserCargoHistorial.unidad_responsable_id == payload.unidad_responsable_id,
            UserCargoHistorial.fecha_fin == None,
            UserCargoHistorial.is_deleted == False
        ).with_for_update(of=UserCargoHistorial, read=True).first()

        if active:
            raise HTTPException(status_code=409, detail="Ya existe una asignación activa para ese cargo y unidad")

        db_obj = UserCargoHistorial(**payload.model_dump(exclude_unset=True))
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)

    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Conflicto al crear la asignación (posible asignación concurrente)")
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error creando asignación: {e}")

    # Audit
    try:
        create_audit_log(db=db, actor_id=current_admin.id, action='create_user_cargo_historial', object_type='user_cargo_historial', object_id=db_obj.id, metadata={'cargo_id': db_obj.cargo_id, 'user_id': db_obj.user_id})
    except Exception:
        pass

    return db_obj


@app.put("/user_cargo_historial/{hist_id}", response_model=UserCargoHistorialResponse, tags=["Cargos"])
def update_user_cargo_historial(hist_id: int, payload: UserCargoHistorialCreate, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    entry = db.query(UserCargoHistorial).filter(UserCargoHistorial.id == hist_id, UserCargoHistorial.is_deleted == False).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    changes = payload.model_dump(exclude_unset=True)
    for k, v in changes.items():
        setattr(entry, k, v)
    db.commit()
    db.refresh(entry)
    try:
        create_audit_log(db=db, actor_id=current_admin.id, action='update_user_cargo_historial', object_type='user_cargo_historial', object_id=entry.id, metadata={'changes': changes})
    except Exception:
        pass
    return entry


@app.delete("/user_cargo_historial/{hist_id}", tags=["Cargos"])
def delete_user_cargo_historial(hist_id: int, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    entry = db.query(UserCargoHistorial).filter(UserCargoHistorial.id == hist_id, UserCargoHistorial.is_deleted == False).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    entry.is_deleted = True
    db.commit()
    try:
        create_audit_log(db=db, actor_id=current_admin.id, action='delete_user_cargo_historial', object_type='user_cargo_historial', object_id=hist_id)
    except Exception:
        pass
    return {"message": "Historial marcado como eliminado"}


# -----------------------------------------------------------------------------
# Endpoints auxiliares para asignación/desasignación por conveniencia (wrap)
# -----------------------------------------------------------------------------
from pydantic import BaseModel as PydanticBaseModel

class CargoAssignPayload(PydanticBaseModel):
    cargo_id: int
    user_id: int
    unidad_responsable_id: int
    motivo: str | None = None

class CargoUnassignPayload(PydanticBaseModel):
    hist_id: int | None = None
    cargo_id: int | None = None
    unidad_responsable_id: int | None = None


@app.post("/cargos/asignar", response_model=UserCargoHistorialResponse, tags=["Cargos"], summary="Asignar cargo a usuario (transaccional)")
def asignar_cargo_api(payload: CargoAssignPayload, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    # Reuse transactional logic from create_user_cargo_historial
    body = UserCargoHistorialCreate(
        cargo_id=payload.cargo_id,
        user_id=payload.user_id,
        unidad_responsable_id=payload.unidad_responsable_id,
        motivo=payload.motivo
    )
    return create_user_cargo_historial(body, db=db, current_admin=current_admin)


@app.post("/cargos/desasignar", tags=["Cargos"], summary="Finalizar asignación activa (set fecha_fin)")
def desasignar_cargo_api(payload: CargoUnassignPayload, db: Session = Depends(get_db), current_admin: User = Depends(get_admin_user)):
    from sqlalchemy import select
    # determinar el registro a cerrar
    if payload.hist_id:
        entry = db.query(UserCargoHistorial).filter(UserCargoHistorial.id == payload.hist_id, UserCargoHistorial.is_deleted == False).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Historial no encontrado")
    else:
        if not (payload.cargo_id and payload.unidad_responsable_id):
            raise HTTPException(status_code=400, detail="Proporciona hist_id o (cargo_id + unidad_responsable_id)")
        entry = db.query(UserCargoHistorial).filter(
            UserCargoHistorial.cargo_id == payload.cargo_id,
            UserCargoHistorial.unidad_responsable_id == payload.unidad_responsable_id,
            UserCargoHistorial.fecha_fin == None,
            UserCargoHistorial.is_deleted == False
        ).first()
        if not entry:
            raise HTTPException(status_code=404, detail="No existe una asignación activa para ese cargo/unidad")

    # cerrar asignación
    entry.fecha_fin = datetime.utcnow()
    db.commit()
    try:
        create_audit_log(db=db, actor_id=current_admin.id, action='cargo_unassign', object_type='user_cargo_historial', object_id=entry.id, metadata={'cargo_id': entry.cargo_id, 'user_id': entry.user_id, 'unidad_responsable_id': entry.unidad_responsable_id})
    except Exception:
        pass
    return {"message": "Asignación finalizada", "hist_id": entry.id}


@app.get(
    "/unidades_responsables/{unidad_id}",
    response_model=UnidadResponsableResponse,
    tags=["Unidades Responsables"]
)
def get_unidad(unidad_id: int, db: Session = Depends(get_db)):
    unidad = (
        db.query(UnidadResponsable)
        .options(joinedload(UnidadResponsable.usuario_responsable))
        .filter(UnidadResponsable.id_unidad == unidad_id)
        .first()
    )
    if not unidad:
        raise HTTPException(status_code=404, detail="Unidad no encontrada")

    # arma objeto embebido si existe
    resp_obj = None
    if unidad.usuario_responsable:
        resp_obj = UserResponse(
            id=unidad.usuario_responsable.id,
            username=unidad.usuario_responsable.username,
            email=unidad.usuario_responsable.email,
            role=unidad.usuario_responsable.role,
            is_deleted=unidad.usuario_responsable.is_deleted,
        )

    # ⚠️ importante: no sobrescribas unidad.responsable con objeto si tu modelo lo usa como int.
    # devuelve un dict compatible con schema:
    return {
        "id_unidad": unidad.id_unidad,
        "nombre": unidad.nombre,
        "telefono": unidad.telefono,
        "domicilio": unidad.domicilio,
        "municipio": unidad.municipio,
        "localidad": unidad.localidad,
        "codigo_postal": unidad.codigo_postal,
        "rfc": unidad.rfc,
        "correo_electronico": unidad.correo_electronico,
        "tipo_unidad": unidad.tipo_unidad,
        "fecha_creacion": unidad.fecha_creacion,
        "unidad_padre_id": unidad.unidad_padre_id,
        "responsable_id": unidad.responsable,   # int
        "responsable": resp_obj,                # objeto o None
    }

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


# =================================================================================================
#                                   ACTAS DE ENTREGA RECEPCIÓN
# =================================================================================================
@app.get("/actas", response_model=List[ActaResponse], tags=["Actas de Entrega Recepción"])
def read_actas(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    try:
        actas = (
            db.query(ActaEntregaRecepcion)
            .options(
                selectinload(ActaEntregaRecepcion.unidad),
                selectinload(ActaEntregaRecepcion.anexos)
            )
            .offset(skip)
            .limit(limit)
            .all()
        )
        if not actas:
            return []
            # 👇 Agrega esto para depurar
        for i, acta in enumerate(actas):
            print(f"\n--- Acta {i} ---")
            for j, anexo in enumerate(acta.anexos):
                print(f"Anexo {j} tipo: {type(anexo.datos)}")
                print(f"Anexo {j} contenido: {anexo.datos}")
        
        return actas  # FastAPI intentará serializar esto
        # return actas
    except Exception as e:
        print(f"Error detallado en /actas: {type(e).__name__}: {e}")  # Log clave
        raise HTTPException(status_code=500, detail=f"Error interno: {str(e)}")


@app.get("/actas/{acta_id}", response_model=ActaResponse, tags=["Actas de Entrega Recepción"])
def read_acta(acta_id: int, db: Session = Depends(get_db)):
    db_acta = (
        db.query(ActaEntregaRecepcion)
        .options(selectinload(ActaEntregaRecepcion.anexos))
        .filter(ActaEntregaRecepcion.id == acta_id)
        .first()
    )
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    return db_acta

@app.post("/actas", response_model=ActaResponse, status_code=status.HTTP_201_CREATED, tags=["Actas de Entrega Recepción"])
def crear_acta(acta: ActaCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), request: Request = None):
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
        anexos_a_asociar = db.query(Anexos).filter(
            Anexos.unidad_responsable_id == acta.unidad_responsable,
            Anexos.creador_id == current_user.id,
            ((Anexos.acta_id == None) | (Anexos.acta_id == 0))
        ).all()
        for an in anexos_a_asociar:
            an.acta_id = db_acta.id
        db.commit()
        db.refresh(db_acta)
        if db_acta.creado_en is None:
            db_acta.creado_en = datetime.utcnow()
        if db_acta.actualizado_en is None:
            db_acta.actualizado_en = datetime.utcnow()
            
        db.commit()
        db.refresh(db_acta)
        db_acta = (
            db.query(ActaEntregaRecepcion)
            .options(selectinload(ActaEntregaRecepcion.anexos))
            .filter(ActaEntregaRecepcion.id == db_acta.id)
            .first()
        )

        # Auditoría
        try:
            logger.info(f"[AUDIT] Attempting to create audit log for acta {db_acta.id} by actor {current_user.id if current_user else None}")
            audit_res = create_audit_log(
                db=db,
                actor_id=current_user.id if current_user else None,
                action='create_acta',
                object_type='acta',
                object_id=db_acta.id,
                metadata={'folio': db_acta.folio, 'unidad_responsable': db_acta.unidad_responsable},
                ip=(request.state.client_ip if request else None)
            )
            logger.info(f"[AUDIT] create_audit_log returned: {audit_res}")
            # Si por alguna razón el helper falló silenciosamente, crear el registro manualmente
            if audit_res is None:
                from .models import AuditLog
                fallback = AuditLog(
                    actor_id=current_user.id if current_user else None,
                    action='create_acta',
                    object_type='acta',
                    object_id=db_acta.id,
                    ip_address=(request.state.client_ip if request else None),
                    metadata_json={'folio': db_acta.folio}
                )
                db.add(fallback)
                db.commit()
                logger.info(f"[AUDIT] Fallback audit log created for acta {db_acta.id}")
        except Exception as e:
            logger.exception(f"Error creating audit log for acta {db_acta.id}: {e}")
            pass

        return db_acta
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error al crear acta: {str(e)}")

@app.put("/actas/{acta_id}", response_model=ActaResponse, tags=["Actas de Entrega Recepción"])
def update_acta(acta_id: int, acta: ActaUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), request: Request = None):
    db_acta = db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.id == acta_id).first()
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")

    changes = acta.model_dump(exclude_unset=True)
    for key, value in changes.items():
        setattr(db_acta, key, value)
    db.commit()
    db.refresh(db_acta)

    # Auditoría
    try:
        create_audit_log(
            db=db,
            actor_id=current_user.id if current_user else None,
            action='update_acta',
            object_type='acta',
            object_id=db_acta.id,
            metadata={'changes': changes},
            ip=(request.state.client_ip if request else None)
        )
    except Exception:
        pass

    return db_acta


@app.delete("/actas/{acta_id}", tags=["Actas de Entrega Recepción"])
def delete_acta(acta_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), request: Request = None):
    db_acta = db.query(ActaEntregaRecepcion).filter(
        ActaEntregaRecepcion.id == acta_id
    ).first()
    
    if not db_acta:
        raise HTTPException(status_code=404, detail="Acta no encontrada")
    
    # Opción 1: Eliminación real
    db.delete(db_acta)
    db.commit()

    # Auditoría
    try:
        create_audit_log(
            db=db,
            actor_id=current_user.id if current_user else None,
            action='delete_acta',
            object_type='acta',
            object_id=acta_id,
            metadata={'folio': db_acta.folio},
            ip=(request.state.client_ip if request else None)
        )
    except Exception:
        pass

    return {"message": "Acta eliminada correctamente"}

# =================================================================================================
#                                           AUDIT LOGS
# =================================================================================================
@app.get('/admin/audit_logs', tags=['Admin', 'Audit'], response_model=dict)
def get_audit_logs(
    actor_id: int | None = None,
    object_type: str | None = None,
    action: str | None = None,
    start_ts: str | None = None,
    end_ts: str | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_admin_user)
):
    """Devuelve logs de auditoría en formato JSON plano con metadatos.

    Filtros soportados: actor_id, object_type, action, start_ts, end_ts, skip, limit
    """
    # Permite al admin consultar logs con filtros y devuelve metadata correctamente
    query = db.query(AuditLog)
    if actor_id is not None:
        query = query.filter(AuditLog.actor_id == actor_id)
    if object_type is not None:
        query = query.filter(AuditLog.object_type == object_type)
    if action is not None:
        query = query.filter(AuditLog.action == action)
    # start_ts / end_ts aceptan ISO timestamps o fechas
    if start_ts:
        try:
            query = query.filter(AuditLog.timestamp >= start_ts)
        except Exception:
            pass
    if end_ts:
        try:
            query = query.filter(AuditLog.timestamp <= end_ts)
        except Exception:
            pass

    total = query.count()
    results = query.order_by(AuditLog.timestamp.desc()).offset(skip).limit(limit).all()

    # Convertir resultados a estructuras JSON serializables
    from fastapi.encoders import jsonable_encoder
    items = []
    for r in results:
        # metadata_json puede ser JSON o None
        metadata = None
        if hasattr(r, 'metadata_json') and r.metadata_json is not None:
            metadata = r.metadata_json
        item = {
            'id': r.id,
            'actor_id': r.actor_id,
            'action': r.action,
            'object_type': r.object_type,
            'object_id': r.object_id,
            'timestamp': r.timestamp.isoformat() if r.timestamp else None,
            'success': r.success,
            'ip_address': r.ip_address,
            'metadata': metadata
        }
        items.append(item)

    return {"total": total, "items": items}

# =================================================================================================
#                                   ANEXOS DE ENTREGA RECEPCIÓN
# =================================================================================================
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
def create_anexo(anexo: AnexoCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), request: Request = None):
    
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

    # Auditoría
    try:
        create_audit_log(
            db=db,
            actor_id=current_user.id if current_user else None,
            action='create_anexo',
            object_type='anexo',
            object_id=db_anexo.id,
            metadata={'clave': db_anexo.clave, 'unidad_responsable_id': db_anexo.unidad_responsable_id},
            ip=(request.state.client_ip if request else None)
        )
    except Exception:
        pass

    return db_anexo
    
# get by id
@app.get("/anexos/{anexo_id}", response_model=AnexoResponse, tags=["Anexos de Entrega Recepción"])
def read_anexo(anexo_id: int, db: Session = Depends(get_db)):
    db_anexo = db.query(Anexos).filter(Anexos.id == anexo_id, Anexos.is_deleted == False).first()
    if not db_anexo:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")
    return db_anexo

# para actualizar un anexos existente
@app.put("/anexos/{anexo_id}", response_model=AnexoResponse, tags=["Anexos de Entrega Recepción"])
def update_anexo(anexo_id: int, anexo: AnexoUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), request: Request = None):
    db_anexo = db.query(Anexos).filter(Anexos.id == anexo_id, Anexos.is_deleted == False).first()
    if not db_anexo:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")

    changes = anexo.model_dump(exclude_unset=True)

    # Actualizar campos
    for key, value in changes.items():
        setattr(db_anexo, key, value)

    db_anexo.actualizado_en = date.today()
    db.commit()
    db.refresh(db_anexo)

    # Auditoría
    try:
        create_audit_log(
            db=db,
            actor_id=current_user.id if current_user else None,
            action='update_anexo',
            object_type='anexo',
            object_id=db_anexo.id,
            metadata={'changes': changes},
            ip=(request.state.client_ip if request else None)
        )
    except Exception:
        pass

    return db_anexo


# marcar un anexo como eliminado
@app.delete("/anexos/{anexo_id}", tags=["Anexos de Entrega Recepción"])
def delete_anexo(anexo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user), request: Request = None):
    db_anexo = db.query(Anexos).filter(Anexos.id == anexo_id, Anexos.is_deleted == False).first()
    if not db_anexo:
        raise HTTPException(status_code=404, detail="Anexo no encontrado")

    db_anexo.is_deleted = True
    db_anexo.actualizado_en = date.today()
    db.commit()

    # Auditoría
    try:
        create_audit_log(
            db=db,
            actor_id=current_user.id if current_user else None,
            action='delete_anexo',
            object_type='anexo',
            object_id=anexo_id,
            metadata={'clave': db_anexo.clave},
            ip=(request.state.client_ip if request else None)
        )
    except Exception:
        pass

    return {"message": "Anexo eliminado correctamente"}

# endpont para obtener anexos por clave
@app.get("/anexos/clave/{clave}", response_model=List[AnexoResponse], tags=["Anexos de Entrega Recepción"])
def read_anexos_by_clave(clave: str, db: Session = Depends(get_db)):
    try:
        anexos = db.query(Anexos).filter(
            Anexos.clave == clave,
            Anexos.is_deleted == False
        ).all()
        if not anexos:
            return []
        return anexos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar anexos por clave: {str(e)}")
    
    # anexo por estado
@app.get("/anexos/estado/{estado}", response_model=List[AnexoResponse], tags=["Anexos de Entrega Recepción"])
def read_anexos_by_estado(estado: str, db: Session = Depends(get_db)):
    try:
        anexos = db.query(Anexos).filter(
            Anexos.estado == estado,
            Anexos.is_deleted == False
        ).all()
        if not anexos:
            return []
        return anexos
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar anexos por estado: {str(e)}")
    
# Join de anexos por actas

