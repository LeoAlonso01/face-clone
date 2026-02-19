"""
Script de migración para agregar tablas:
- cargos
- user_cargo_historial

Ejecutar con:
    python scripts/migrate_cargos.py migrate
    python scripts/migrate_cargos.py rollback
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.app.database import engine
except ModuleNotFoundError:
    from app.database import engine

from sqlalchemy import text

SQL_CREATE = """
CREATE TABLE IF NOT EXISTS cargos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_cargo_historial (
    id SERIAL PRIMARY KEY,
    cargo_id INTEGER NOT NULL REFERENCES cargos(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    unidad_responsable_id INTEGER NOT NULL REFERENCES unidades_responsables(id_unidad),

    fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP NULL,

    asignado_por_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    motivo TEXT,

    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_cargos_nombre ON cargos(nombre);

CREATE INDEX IF NOT EXISTS idx_user_cargo_historial_user_id
    ON user_cargo_historial(user_id);

CREATE INDEX IF NOT EXISTS idx_user_cargo_historial_unidad
    ON user_cargo_historial(unidad_responsable_id);

CREATE INDEX IF NOT EXISTS idx_user_cargo_historial_cargo
    ON user_cargo_historial(cargo_id);

CREATE INDEX IF NOT EXISTS idx_user_cargo_historial_activos
    ON user_cargo_historial(cargo_id, unidad_responsable_id, fecha_fin);

CREATE UNIQUE INDEX IF NOT EXISTS ux_cargo_unidad_activo
    ON user_cargo_historial(cargo_id, unidad_responsable_id)
    WHERE fecha_fin IS NULL AND is_deleted = FALSE;
"""

SQL_ROLLBACK = """
DROP TABLE IF EXISTS user_cargo_historial CASCADE;
DROP TABLE IF EXISTS cargos CASCADE;
"""

def migrate():
    try:
        with engine.connect() as conn:
            conn.execute(text(SQL_CREATE))
            conn.commit()
            print("✅ Migración cargos + user_cargo_historial completada")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        raise

def rollback():
    try:
        with engine.connect() as conn:
            conn.execute(text(SQL_ROLLBACK))
            conn.commit()
            print("✅ Rollback cargos + user_cargo_historial completado")
    except Exception as e:
        print(f"❌ Error durante el rollback: {e}")
        raise

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Migración de cargos')
    parser.add_argument('action', choices=['migrate', 'rollback'])
    args = parser.parse_args()

    if args.action == 'migrate':
        migrate()
    else:
        rollback()
