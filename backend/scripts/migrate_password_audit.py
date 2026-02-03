"""
Script de migración para agregar tabla de auditoría de contraseñas

Ejecutar con:
    python scripts/migrate_password_audit.py

O ejecutar el SQL directamente en la base de datos
"""

import sys
import os

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from backend.app.database import engine
except ModuleNotFoundError:
    from app.database import engine
from sqlalchemy import text


SQL_CREATE_TABLE = """
-- Crear tabla de logs de auditoría para contraseñas
CREATE TABLE IF NOT EXISTS password_audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (target_user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Crear índices para consultas eficientes
CREATE INDEX IF NOT EXISTS idx_password_audit_admin_id ON password_audit_logs(admin_id);
CREATE INDEX IF NOT EXISTS idx_password_audit_target_user_id ON password_audit_logs(target_user_id);
CREATE INDEX IF NOT EXISTS idx_password_audit_timestamp ON password_audit_logs(timestamp);

-- Comentarios para documentación
COMMENT ON TABLE password_audit_logs IS 'Registro de auditoría para cambios y reseteos de contraseñas';
COMMENT ON COLUMN password_audit_logs.admin_id IS 'ID del administrador que realizó la acción';
COMMENT ON COLUMN password_audit_logs.target_user_id IS 'ID del usuario cuya contraseña fue modificada';
COMMENT ON COLUMN password_audit_logs.action IS 'Tipo de acción: password_change o password_reset';
COMMENT ON COLUMN password_audit_logs.ip_address IS 'Dirección IP desde donde se realizó la acción';
"""


SQL_ROLLBACK = """
-- Rollback: Eliminar tabla de auditoría
DROP TABLE IF EXISTS password_audit_logs CASCADE;
"""


def migrate():
    """Ejecutar migración"""
    try:
        with engine.connect() as conn:
            # Ejecutar la migración
            conn.execute(text(SQL_CREATE_TABLE))
            conn.commit()
            print("✅ Migración completada exitosamente")
            print("✅ Tabla 'password_audit_logs' creada")
            print("✅ Índices creados")
    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        raise


def rollback():
    """Revertir migración"""
    try:
        with engine.connect() as conn:
            conn.execute(text(SQL_ROLLBACK))
            conn.commit()
            print("✅ Rollback completado exitosamente")
            print("✅ Tabla 'password_audit_logs' eliminada")
    except Exception as e:
        print(f"❌ Error durante el rollback: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migración de auditoría de contraseñas')
    parser.add_argument('action', choices=['migrate', 'rollback'], 
                       help='Acción a realizar: migrate o rollback')
    
    args = parser.parse_args()
    
    if args.action == 'migrate':
        print("🚀 Ejecutando migración...")
        migrate()
    elif args.action == 'rollback':
        print("⏪ Ejecutando rollback...")
        rollback()
