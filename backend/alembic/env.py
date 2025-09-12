from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os

# Ajusta la ruta según tu estructura
# Suponiendo: backend/app/models.py
from app.models import User, BaseModel  # Cambia si tu estructura es diferente
import app.models  # Para que SQLAlchemy detecte todas las tablas

config = context.config

# Interpreta el archivo de configuración para Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# URL de la base de datos
# Usa la misma que en tu docker-compose.yml
config.set_main_option(
    "sqlalchemy.url",
    "postgresql://user:password@localhost:5433/facebook_clone"
)

target_metadata = app.models.BaseModel.metadata

def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()