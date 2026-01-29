from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

import os

# Allow overriding the database URL (useful for tests). If DATABASE_URL is provided,
# we don't require the individual POSTGRES_* environment variables to be present.
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    class Settings(BaseSettings):
        POSTGRES_USER: str
        POSTGRES_PASSWORD: str
        POSTGRES_DB: str
        POSTGRES_HOST: str
        POSTGRES_PORT: str
        SENDGRID_API_KEY: Optional[str] = None	

        model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    # Crea una instancia solo si es necesario (opcional)
    try:
        settings = Settings()
    except Exception as e:
        raise RuntimeError(f"Error cargando variables de entorno: {e}")

    DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

# Support for sqlite in-memory for tests
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,           # Número de conexiones mantenidas
        max_overflow=20,        # Máximo que puede crear sobre el pool_size
        pool_timeout=30,        # Tiempo de espera para obtener conexión
        pool_recycle=3600       # Reciclar conexiones después de 1 hora
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Context manager para sesiones
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()