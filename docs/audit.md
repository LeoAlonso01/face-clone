# Auditoría (Audit Logs)

## Resumen
Se añadió una tabla genérica `audit_logs` para registrar acciones críticas del sistema: cambios de contraseña, creación/edición/eliminación de anexos y actas, y otras acciones administrativas.

## Modelo
- `id`
- `actor_id` (FK users.id)
- `action` (string)
- `object_type` (string) - e.g., `user`, `anexo`, `acta`
- `object_id` (integer)
- `timestamp`
- `success` (boolean)
- `ip_address` (string)
- `metadata` (JSON) - datos no sensibles con contexto (ej: campos modificados)

## Endpoints
### Consultar logs (solo ADMIN)
`GET /admin/audit_logs`

Query params opcionales: `actor_id`, `object_type`, `action`, `start_ts`, `end_ts`, `skip`, `limit`

Respuesta: `{ total: int, items: [ AuditLog ] }`

## Implementación técnica
- Nuevo modelo `AuditLog` en `backend/app/models.py`.
- Helper `create_audit_log(db, actor_id, action, object_type, object_id, success, metadata, ip)` en `backend/app/audit.py`.
- Middleware `AuditMiddleware` en `backend/app/middleware.py` que captura `client_ip` y `user_agent` y los pone en `request.state`.
- Endpoints instrumentados:
  - `POST /anexos`, `PUT /anexos/{id}`, `DELETE /anexos/{id}`
  - `POST /actas`, `PUT /actas/{id}`, `DELETE /actas/{id}`
  - `POST /users/{id}/change_password`, `POST /admin/users/{id}/reset_password`
- Migración SQL en `backend/migrations/002_add_audit_logs.sql`.
- Script de migración `backend/scripts/migrate_audit_logs.py` (ejecutar dentro del contenedor con PYTHONPATH si es necesario).

## Notas de seguridad
- No almacenamos contraseñas en `metadata`; el helper sanitiza campos sensibles.
- Se recomienda limitar acceso al endpoint de consulta a administradores y auditores.

## Ejemplos de uso
- Crear un anexo y luego consultar logs para `object_type=anexo`.

## Próximos pasos (recomendados)
- Agregar retención configurable y exportación de logs
- Integrar con SIEM/Elastic Stack para análisis y alertas
- Añadir reportes y vistas en el panel de administrador
