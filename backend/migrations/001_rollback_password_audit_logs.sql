-- ============================================================================
-- Rollback: Eliminar tabla de auditoría de contraseñas
-- Fecha: 2026-02-01
-- Descripción: Revierte la migración 001_add_password_audit_logs
-- ============================================================================

-- Eliminar índices primero
DROP INDEX IF EXISTS idx_password_audit_admin_id;
DROP INDEX IF EXISTS idx_password_audit_target_user_id;
DROP INDEX IF EXISTS idx_password_audit_timestamp;

-- Eliminar tabla
DROP TABLE IF EXISTS password_audit_logs CASCADE;

-- Verificar que la tabla fue eliminada
SELECT table_name 
FROM information_schema.tables 
WHERE table_name = 'password_audit_logs';
-- (Debería retornar 0 filas)
