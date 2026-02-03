-- ============================================================================
-- Migración: Agregar tabla de auditoría de contraseñas
-- Fecha: 2026-02-01
-- Descripción: Crea la tabla password_audit_logs para registrar cambios
--              y reseteos de contraseñas por administradores
-- ============================================================================

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
CREATE INDEX IF NOT EXISTS idx_password_audit_admin_id 
    ON password_audit_logs(admin_id);

CREATE INDEX IF NOT EXISTS idx_password_audit_target_user_id 
    ON password_audit_logs(target_user_id);

CREATE INDEX IF NOT EXISTS idx_password_audit_timestamp 
    ON password_audit_logs(timestamp);

-- Comentarios para documentación
COMMENT ON TABLE password_audit_logs IS 
    'Registro de auditoría para cambios y reseteos de contraseñas';

COMMENT ON COLUMN password_audit_logs.admin_id IS 
    'ID del administrador que realizó la acción';

COMMENT ON COLUMN password_audit_logs.target_user_id IS 
    'ID del usuario cuya contraseña fue modificada';

COMMENT ON COLUMN password_audit_logs.action IS 
    'Tipo de acción: password_change o password_reset';

COMMENT ON COLUMN password_audit_logs.ip_address IS 
    'Dirección IP desde donde se realizó la acción';

-- Verificar que la tabla se creó correctamente
SELECT 
    table_name, 
    column_name, 
    data_type 
FROM information_schema.columns 
WHERE table_name = 'password_audit_logs'
ORDER BY ordinal_position;
