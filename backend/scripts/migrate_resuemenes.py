"""
Script de migración para tabla resumenes

Ejecutar con:
    python scripts/migrate_resumenes.py migrate
"""

from dotenv import load_dotenv


import sys
import os

load_dotenv()

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.app.database import engine
except ModuleNotFoundError:
    from app.database import engine

from sqlalchemy import text

SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS resumenes (
    id SERIAL PRIMARY KEY,
    acta_id INTEGER NOT NULL REFERENCES acta_entrega_recepcion(id) ON DELETE CASCADE,
    file_id VARCHAR(255),
    url TEXT NOT NULL,
    nombre_archivo VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resumenes_acta_id ON resumenes(acta_id);
"""

SQL_ROLLBACK = """
DROP TABLE IF EXISTS resumenes CASCADE;
"""


def migrate():
    try:
        with engine.connect() as conn:
            conn.execute(text(SQL_CREATE_TABLE))
            conn.commit()
            print("✅ Migración resumenes completada")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        raise


def rollback():
    try:
        with engine.connect() as conn:
            conn.execute(text(SQL_ROLLBACK))
            conn.commit()
            print("✅ Rollback resumenes completado")
    except Exception as e:
        print(f"❌ Error durante el rollback: {e}")
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Migración de resumenes')
    parser.add_argument('action', choices=['migrate', 'rollback'])
    args = parser.parse_args()

    if args.action == 'migrate':
        migrate()
    else:
        rollback()