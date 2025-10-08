from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: str

    model_config = SettingsConfigDict(env_file=".env")

# Crea una instancia solo si es necesario (opcional)
try:
    settings = Settings()
except Exception as e:
    raise RuntimeError(f"Error cargando variables de entorno: {e}")

DATABASE_URL = f"postgresql://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_DB}"

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