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
    # Configuración para entorno de producción con SendGrid
    SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
    
    # Si no hay API key configurada, usar modo simulado
    if not SENDGRID_API_KEY:
        print(f"📧 [Simulado] Enviando correo a {destinatario}")
        print(f"Hola {nombre_usuario}, usa este token: {token}")
        print(f"Enlace: http://localhost:3000/reset-password?token={token}")
        print("⚠️ SENDGRID_API_KEY no configurada. No se envió ningún correo real.")
        return
    
    # Envío real con SendGrid
    try:
        from sendgrid import SendGridAPIClient
        from sendgrid.helpers.mail import Mail, Email, To, Content
        
        # Crear el mensaje
        from_email = Email("no-reply@umich.mx")  # Cambiar por tu email verificado en SendGrid
        to_email = To(destinatario)
        subject = "Recuperación de contraseña - Sistema UMICH"
        
        # Plantilla HTML del email
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2c5aa0; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: #f9f9f9; padding: 30px; border-radius: 5px; }}
                .token {{ background-color: #eee; padding: 15px; border-radius: 5px; font-family: monospace; font-size: 16px; }}
                .button {{ background-color: #2c5aa0; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Recuperación de Contraseña</h1>
                </div>
                <div class="content">
                    <h2>Hola {nombre_usuario},</h2>
                    <p>Has solicitado restablecer tu contraseña en el Sistema de la Universidad Michoacana.</p>
                    
                    <p><strong>Token de recuperación:</strong></p>
                    <div class="token">{token}</div>
                    
                    <p>O haz clic en el siguiente enlace:</p>
                    <a href="http://localhost:3000/reset-password?token={token}" class="button">
                        Restablecer Contraseña
                    </a>
                    
                    <p style="margin-top: 30px; color: #666; font-size: 14px;">
                        ⚠️ Este token expirará en 1 hora. Si no solicitaste este cambio, ignora este mensaje.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        content = Content("text/html", html_content)
        mail = Mail(from_email, to_email, subject, content)
        
        # Enviar el email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(mail)
        
        print(f"✅ Email enviado exitosamente a {destinatario}")
        print(f"Status Code: {response.status_code}")
        
    except Exception as e:
        print(f"❌ Error enviando email a {destinatario}: {e}")
        # Fallback: mostrar info en consola
        print(f"📧 [Fallback] Token para {nombre_usuario}: {token}")
        print(f"📧 [Fallback] Enlace: http://localhost:3000/reset-password?token={token}")
