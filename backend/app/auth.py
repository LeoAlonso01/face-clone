from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session, joinedload
from .database import get_db
from .models import User, UserRoles
import os


# Configuración de seguridad
SECRET_KEY = "tu_clave_secreta"  # Cambia esto por una clave segura en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(User).filter(User.username == username, User.is_deleted == False).first()
    if not user or not verify_password(password, user.password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
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

    # Carga la relación correcta con la unidad responsable
    user = db.query(User).options(
        joinedload(User.unidad)
    ).filter(User.username == username).first()
    
    if user is None:
        raise credentials_exception
    return user

def get_admin_user(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRoles.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden realizar esta acción"
        )
    return current_user

# services/email_service.py
def enviar_email_recuperacion(destinatario: str, nombre_usuario: str, token: str):
    # 🔜 Aquí integraremos Resend, Gmail, etc.
    # Por ahora, solo registramos
    print(f"📧 [Simulado] Enviando correo a {destinatario}")
    print(f"Hola {nombre_usuario}, usa este token: {token}")
    print(f"Enlace: http://localhost:3000/reset-password?token={token}")
    print("⚠️ Este es un entorno de desarrollo. No se envió ningún correo real.")
