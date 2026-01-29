from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..auth import get_current_user, get_admin_user, authenticate_user, create_access_token
from ..schemas import UserCreate, UserResponse, UserUpdate, ForgotPasswordRequest, ChangePasswordRequest
from ..database import get_db
from ..models import User
from ..auth import get_password_hash, enviar_email_recuperacion, verify_password
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import BackgroundTasks

router = APIRouter(tags=["Usuario"])  # Keep root-level paths (/register, /token, /users, etc.) for backward compatibility

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El nombre de usuario ya está en uso")
    existing_email = db.query(User).filter(User.email == user.email).first()
    if existing_email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El correo electrónico ya está en uso")
    hashed_password = get_password_hash(user.password)
    db_user = User(username=user.username, email=user.email, password=hashed_password, is_deleted=False, role=None)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "Usuario registrado exitosamente", "user": {"id": db_user.id, "username": db_user.username, "email": db_user.email}}

@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Nombre de usuario o contraseña incorrectos")
    if user.role is None:
        raise HTTPException(status_code=403, detail="Este usuario aun no tiene un rol asignado, Solicta acceso a un administrador")
    if user.is_deleted:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario eliminado, no puedes iniciar sesión")
    access_token = create_access_token(data={"sub": user.username, "user_id": user.id, "email": user.email, "username": user.username, "role": user.role.value if hasattr(user.role, 'value') else user.role})
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "username": user.username, "email": user.email, "role": user.role}

@router.get("/users", response_model=list[UserResponse])
def get_users(skip: int = 0, limit: int = 1000, db: Session = Depends(get_db)):
    users = db.query(User).filter(User.is_deleted == False).offset(skip).limit(limit).all()
    return users

@router.get("/users/{user_id}")
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

@router.delete("/users/{user_id}")
def soft_delete_user(user_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_admin_user)):
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    user.is_deleted = True
    db.commit()
    return {"message": "Usuario marcado como eliminado"}

@router.put("/users/{user_id}/change-password")
def change_password(user_id: int, password_data: ChangePasswordRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.id != user_id and (current_user.role != "ADMIN" and getattr(current_user.role, 'value', current_user.role) != "ADMIN"):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permisos para cambiar la contraseña de otro usuario")
    user = db.query(User).filter(User.id == user_id, User.is_deleted == False).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if not verify_password(password_data.current_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contraseña actual incorrecta")
    if verify_password(password_data.new_password, user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La nueva contraseña no puede ser igual a la actual")
    user.password = get_password_hash(password_data.new_password)
    db.commit()
    db.refresh(user)
    return {"message": "Contraseña actualizada exitosamente"}

@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email, User.is_deleted == False).first()
    if not user:
        return {"message": "Si el email está registrado, recibirás instrucciones para recuperar tu contraseña."}
    token = "".join(__import__('secrets').choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(32))
    from datetime import datetime, timedelta
    expires_at = datetime.utcnow() + timedelta(minutes=15)
    user.reset_token = token
    user.reset_token_expiration = expires_at
    db.commit()
    try:
        background_tasks.add_task(enviar_email_recuperacion, destinatario=user.email, nombre_usuario=user.username, token=token)
    except Exception:
        pass
    return {"message": "Si el email está registrado, recibirás instrucciones para recuperar tu contraseña."}
