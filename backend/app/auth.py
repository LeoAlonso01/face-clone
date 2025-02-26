from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User, UserRoles
from passlib.context import CryptContext

# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta"  # Cambia esto por una clave segura en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Función para verificar la contraseña
def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

# Función para obtener el hash de la contraseña
def get_password_hash(password: str):
    return pwd_context.hash(password)

# Función para autenticar al usuario
def authenticate_user(db: Session, username: str, password: str):
    # Buscar el usuario en la base de datos
    user = db.query(User).filter(User.username == username, User.is_deleted == False).first()
    
    # Verificar si el usuario existe y si la contraseña es correcta
    if not user or not verify_password(password, user.password):
        return False  # Credenciales inválidas
    
    return user  # Credenciales válidas

# Función para crear un token de acceso
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Función para obtener el usuario actual
def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

# Función para obtener el usuario administrador
def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden realizar esta acción"
        )
    return current_user