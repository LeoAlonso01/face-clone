# utils/email.py
import resend
import os
from datetime import datetime

resend.api_key = os.getenv("RESEND_API_KEY")

def enviar_email_recuperacion(destinatario: str, nombre_usuario: str, token: str):
    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
    reset_link = f"{frontend_url}/reset-password?token={token}"

    html_content = f"""
    <h2>Recuperación de contraseña</h2>
    <p>Hola {nombre_usuario},</p>
    <p>Hemos recibido una solicitud para restablecer tu contraseña.</p>
    <p>Haz clic en el siguiente enlace para crear una nueva contraseña:</p>
    <a href="{reset_link}" style="display:inline-block;padding:10px 20px;background-color:#751518;color:white;text-decoration:none;border-radius:5px;">
        Restablecer contraseña
    </a>
    <p>Este enlace expira en 15 minutos.</p>
    <p>Si no solicitaste este cambio, ignora este correo.</p>
    """

    try:
        resend.Emails.send({
            "from": "noreply@tudominio.com",  # Debe ser un dominio verificado en Resend
            "to": [destinatario],
            "subject": "Restablece tu contraseña - SERUMICH V2",
            "html": html_content
        })
        print(f"[INFO] Correo enviado a {destinatario}")
    except Exception as e:
        print(f"[ERROR] Falló el envío de correo: {e}")
        raise