from fastapi import FastAPI, HTTPException, Depends, status, Body
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from .database import Base, engine, SessionLocal
from sqlalchemy import create_engine, text
from contextlib import asynccontextmanager
from datetime import timedelta
from .auth import (
    authenticate_user,
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
    get_admin_user
)
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # Define the expiration time for the access token
from .models import User, UserRoles
from .database import SessionLocal, engine, Base
from sqlalchemy.orm import Session
USER = "USER"
ADMIN = "ADMIN"

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)


# ruta principal
@app.get("/")
def read_root():
    return {"message": "Bienvenido a Facebook Clone!"}

# ruta para traer datos de contraloria
@app.get("/usuarios_contraloria")
def contraloria_users():
    users = []
    # conexion a la bd postgres local
    db = f"postgresql://contraloria:c0ntr4l0r14@host.docker.internal:5432/contraloria"
    # consulta a la bd local
    try:
        engine = create_engine(db)
        with engine.connect() as connection:
            query = text("SELECT nombre, email, username FROM public.viewmat_situm_dep_usuarios")
            result = connection.execute(query)
            # Obtener los nombres de las columnas
            columns = result.keys()
            # Convertir los resultados en una lista de diccionarios
            users = [dict(zip(columns, row)) for row in result.fetchall()]
    except Exception as e:
        print(e)
    return users
    
# Ruta para el registro de usuarios
@app.post("/register")
def register(username: str, email: str, password: str, role: UserRoles = UserRoles.USER):  # Usa UserRoles.USER
    db = SessionLocal()
    hashed_password = get_password_hash(password)
    db_user = User(username=username, email=email, password=hashed_password, role=role)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Usuario registrado exitosamente"}

# Ruta para el inicio de sesión
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = SessionLocal()
    
    # Autenticar al usuario
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
        )
    
    # Crear el token de acceso
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "user_id": user.id},  # Agrega el ID del usuario
        expires_delta=access_token_expires
    )
    
    # Devolver la respuesta
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }

# ruta para obtener todos los usuarios
@app.get("/users")
def get_users(skip: int = 0, limit: int = 10, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    users = db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
    return users

# ruta para obtener un usuario por ID
@app.get("/users/{user_id}")
def read_user(user_id: int, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return current_user

# ruta para hacer un softdelete de un usuario
@app.delete("/users/{user_id}")
def soft_delete_user(user_id: int, current_user: User = Depends(get_admin_user)):
    db = SessionLocal()
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    user.is_deleted = True
    db.commit()
    return {"message": "Usuario marcado como eliminado"}

# ruta para acttualizar la contraseña de un usuario
@app.put("/users/{user_id}/change-password")
def change_password(
    user_id: int,
    current_password: str = Body(...),
    new_password: str = Body(...),
    current_user: User = Depends(get_current_user),  # Verifica que el usuario esté autenticado
):
    db = SessionLocal()
    
    # Buscar al usuario en la base de datos
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    # Verificar que la contraseña actual sea correcta
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

    # Actualizar la contraseña
    user.password = get_password_hash(new_password)
    db.commit()

    print(f"Usuario autenticado: {current_user.username}")
    print(f"Usuario a modificar: {user.username}")
    print(f"Contraseña actual correcta: {verify_password(current_password, user.password)}")
    
    return {"message": "Contraseña actualizada exitosamente"}

# ruta protegida para obtener informacion de usuario
@app.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user