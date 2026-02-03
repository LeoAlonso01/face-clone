-- ============================================================================
-- Migración: Agregar tabla genérica de auditoría (audit_logs)
-- Fecha: 2026-02-02
-- Descripción: Crea la tabla audit_logs para registrar eventos de auditoría
-- ============================================================================

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

-- Índices para consultas rápidas
CREATE INDEX IF NOT EXISTS idx_audit_actor_id ON audit_logs(actor_id);
CREATE INDEX IF NOT EXISTS idx_audit_object ON audit_logs(object_type, object_id);
CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp);

COMMENT ON TABLE audit_logs IS 'Registro genérico de auditoría para acciones de usuarios (create/update/delete,password reset, etc.)';
