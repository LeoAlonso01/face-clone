from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

import os

class Settings(BaseSettings):
    POSTGRES_USER: str | None = None
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_DB: str | None = None
    POSTGRES_HOST: str | None = None
    POSTGRES_PORT: str | None = None
    SENDGRID_API_KEY: Optional[str] = None

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

# If a DATABASE_URL env var is provided (useful for tests), use it.
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Carga las variables de entorno de postgres solo si DATABASE_URL no está definido
    try:
        settings = Settings()
    except Exception as e:
        raise RuntimeError(f"Error cargando variables de entorno: {e}")

    if not (settings.POSTGRES_USER and settings.POSTGRES_PASSWORD and settings.POSTGRES_DB and settings.POSTGRES_HOST and settings.POSTGRES_PORT):
        raise RuntimeError("Faltan variables de entorno de Postgres y no se encontro DATABASE_URL")

    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Para sqlite, necesitamos pasar connect_args
connect_args = {}
if DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

engine_kwargs = {}
if connect_args:
    engine_kwargs['connect_args'] = connect_args

if not DATABASE_URL.startswith("sqlite"):
    engine_kwargs.update({
        'pool_size': 10,
        'max_overflow': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
    })

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Context manager para sesiones
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()