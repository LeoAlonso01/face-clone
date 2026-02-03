"""
Script de migración para agregar tabla de auditoría genérica audit_logs

Ejecutar con:
    python scripts/migrate_audit_logs.py migrate

"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.app.database import engine
except ModuleNotFoundError:
    from app.database import engine

from sqlalchemy import text

SQL_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS audit_logs (
    id SERIAL PRIMARY KEY,
    actor_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    action VARCHAR(100) NOT NULL,
    object_type VARCHAR(50),
    object_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    ip_address VARCHAR(50),
    metadata JSON
);

CREATE INDEX IF NOT EXISTS idx_audit_actor_id ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_object ON audit_logs(object_type, object_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);
"""

SQL_ROLLBACK = """
DROP TABLE IF EXISTS audit_logs CASCADE;
"""


def migrate():
    try:
        with engine.connect() as conn:
            conn.execute(text(SQL_CREATE_TABLE))
            conn.commit()
            print("✅ Migración audit_logs completada")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        raise


def rollback():
    try:
        with engine.connect() as conn:
            conn.execute(text(SQL_ROLLBACK))
            conn.commit()
            print("✅ Rollback audit_logs completado")
    except Exception as e:
        print(f"❌ Error durante el rollback: {e}")
        raise


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Migración de audit_logs')
    parser.add_argument('action', choices=['migrate', 'rollback'])
    args = parser.parse_args()

    if args.action == 'migrate':
        migrate()
    else:
        rollback()
