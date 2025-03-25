from fastapi import FastAPI, HTTPException, Depends, status, Body 
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import Base, engine
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
    get_admin_user
)
ACCESS_TOKEN_EXPIRE_MINUTES = 30
from .models import User, UserRoles
from .database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
from contextlib import contextmanager

USER = "USER"
ADMIN = "ADMIN"

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

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Bienvenido a Facebook Clone!"}

@app.get("/usuarios_contraloria")
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
    
@app.post("/register")
def register(username: str, email: str, password: str, role: UserRoles = UserRoles.USER):
    with session_scope() as db:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.username == username).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El nombre de usuario ya está en uso"
            )
            
        existing_email = db.query(User).filter(User.email == email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El correo electrónico ya está en uso"
            )
            
        hashed_password = get_password_hash(password)
        db_user = User(username=username, email=email, password=hashed_password, role=role)
        db.add(db_user)
        db.flush()  # Para obtener el ID si es necesario
        return {"message": "Usuario registrado exitosamente"}

@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with session_scope() as db:
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Nombre de usuario o contraseña incorrectos",
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

@app.get("/users")
def get_users(skip: int = 0, limit: int = 10, current_user: User = Depends(get_current_user)):
    with session_scope() as db:
        users = db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
        return [user.to_dict() for user in users]

@app.get("/users/{user_id}")
def read_user(user_id: int, current_user: User = Depends(get_current_user)):
    with session_scope() as db:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return user.to_dict()

@app.delete("/users/{user_id}")
def soft_delete_user(user_id: int, current_user: User = Depends(get_admin_user)):
    with session_scope() as db:
        user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuario no encontrado",
            )
        user.is_deleted = True
        return {"message": "Usuario marcado como eliminado"}

@app.put("/users/{user_id}/change-password")
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

        if not verify_password(current_password, user.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Contraseña actual incorrecta",
            )
        
        if current_user.id != user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No tienes permiso para realizar esta acción",
            )

        user.password = get_password_hash(new_password)
        return {"message": "Contraseña actualizada exitosamente"}

@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()