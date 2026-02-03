# Endpoints de Gestión de Contraseñas

## 🚀 Resumen

Se han implementado dos nuevos endpoints para gestión de contraseñas:

1. **`POST /users/{user_id}/change_password`** - Permite a usuarios cambiar su propia contraseña
2. **`POST /admin/users/{user_id}/reset_password`** - Permite a admins resetear contraseñas de usuarios

## 📦 Archivos Modificados/Creados

### Archivos Modificados:
- ✅ `backend/app/main.py` - Nuevos endpoints implementados
- ✅ `backend/app/schemas.py` - Nuevos schemas: `ResetPasswordRequest`, `PasswordChangeResponse`
- ✅ `backend/app/models.py` - Nuevo modelo: `PasswordAuditLog`

### Archivos Creados:
- ✅ `docs/password-management.md` - Documentación completa de los endpoints
- ✅ `backend/migrations/001_add_password_audit_logs.sql` - Migración SQL
- ✅ `backend/migrations/001_rollback_password_audit_logs.sql` - Rollback SQL
- ✅ `backend/scripts/migrate_password_audit.py` - Script Python para migración
- ✅ `backend/PASSWORD_ENDPOINTS.md` - Este archivo

## 🗃️ Migración de Base de Datos

Antes de usar los nuevos endpoints, debes crear la tabla de auditoría.

### Opción 1: SQL Directo (Recomendado)

Conectarte a tu base de datos PostgreSQL y ejecutar:

```bash
psql -U tu_usuario -d tu_base_de_datos -f backend/migrations/001_add_password_audit_logs.sql
```

O desde psql:
```sql
\i backend/migrations/001_add_password_audit_logs.sql
```

### Opción 2: Script Python

```bash
cd backend
python scripts/migrate_password_audit.py migrate
```

Para revertir:
```bash
python scripts/migrate_password_audit.py rollback
```

### Opción 3: Alembic (si está configurado)

```bash
cd backend
alembic revision --autogenerate -m "Add password audit logs"
alembic upgrade head
```

## 📖 Uso de los Endpoints

### 1. Cambiar Contraseña (Usuario/Admin)

**Endpoint:** `POST /users/{user_id}/change_password`

**Headers:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "current_password": "contraseñaActual123",
  "new_password": "nuevaContraseña456!"
}
```

**Ejemplo cURL:**
```bash
curl -X POST "http://localhost:8000/users/1/change_password" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "oldPass123",
    "new_password": "newPass456!"
  }'
```

**Respuesta Exitosa:**
```json
{
  "message": "Contraseña actualizada exitosamente",
  "success": true
}
```

### 2. Resetear Contraseña (Solo Admin)

**Endpoint:** `POST /admin/users/{user_id}/reset_password`

**Headers:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Body:**
```json
{
  "new_password": "user123"
}
```

**Ejemplo cURL:**
```bash
curl -X POST "http://localhost:8000/admin/users/5/reset_password" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIs..." \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "user123"
  }'
```

**Respuesta Exitosa:**
```json
{
  "message": "Contraseña reseteada exitosamente para el usuario juan.perez",
  "success": true
}
```

## 🔒 Seguridad Implementada

### ✅ Características de Seguridad

1. **Hashing con bcrypt**
   - Cost factor: 12
   - Salt automático

2. **Validación de Permisos**
   - Usuarios solo pueden cambiar su propia contraseña
   - Solo admins pueden usar el endpoint de reset

3. **Auditoría Completa**
   - Cada acción de admin se registra en `password_audit_logs`
   - Incluye: admin_id, target_user_id, timestamp, action

4. **Validación de Contraseñas**
   - Mínimo 8 caracteres
   - Validación de contraseña actual antes de cambiar
   - No permite usar la misma contraseña

5. **Logs del Sistema**
   - Registro detallado de todas las operaciones
   - NO se registran contraseñas en texto plano

## 🧪 Testing

### Probar con Postman/Insomnia

1. **Login para obtener token:**
```
POST http://localhost:8000/token
Body (form-data):
  username: tu_usuario
  password: tu_contraseña
```

2. **Cambiar contraseña:**
```
POST http://localhost:8000/users/1/change_password
Headers:
  Authorization: Bearer <token_obtenido>
  Content-Type: application/json
Body (JSON):
{
  "current_password": "oldPass",
  "new_password": "newPass123!"
}
```

3. **Resetear contraseña (como admin):**
```
POST http://localhost:8000/admin/users/5/reset_password
Headers:
  Authorization: Bearer <admin_token>
  Content-Type: application/json
Body (JSON):
{
  "new_password": "user123"
}
```

### Casos de Prueba

#### ✅ Casos Exitosos
- [ ] Usuario cambia su propia contraseña
- [ ] Admin cambia contraseña de otro usuario (usando change_password)
- [ ] Admin resetea contraseña de usuario (usando reset_password)
- [ ] Se registra auditoría correctamente

#### ❌ Casos de Error
- [ ] Contraseña actual incorrecta → 400
- [ ] Nueva contraseña muy corta → 400
- [ ] Usuario intenta cambiar contraseña de otro → 403
- [ ] No-admin intenta usar endpoint de reset → 403
- [ ] Usuario no existe → 404
- [ ] Token inválido/expirado → 401

## 📊 Consultas de Auditoría Útiles

### Ver todos los cambios realizados por un admin
```sql
SELECT 
    pal.id,
    u1.username as admin,
    u2.username as usuario_afectado,
    pal.action,
    pal.timestamp
FROM password_audit_logs pal
JOIN users u1 ON pal.admin_id = u1.id
JOIN users u2 ON pal.target_user_id = u2.id
WHERE pal.admin_id = 1
ORDER BY pal.timestamp DESC;
```

### Actividad reciente (últimas 24 horas)
```sql
SELECT 
    u1.username as admin,
    u2.username as usuario,
    pal.action,
    pal.timestamp
FROM password_audit_logs pal
JOIN users u1 ON pal.admin_id = u1.id
JOIN users u2 ON pal.target_user_id = u2.id
WHERE pal.timestamp > NOW() - INTERVAL '24 hours'
ORDER BY pal.timestamp DESC;
```

### Historial de un usuario específico
```sql
SELECT 
    u1.username as modificado_por,
    pal.action,
    pal.timestamp
FROM password_audit_logs pal
JOIN users u1 ON pal.admin_id = u1.id
WHERE pal.target_user_id = 5
ORDER BY pal.timestamp DESC;
```

## 🐛 Troubleshooting

### Error: "Solo los administradores pueden realizar esta acción"
**Causa:** El token no tiene rol ADMIN  
**Solución:** Verificar rol del usuario en la BD:
```sql
SELECT id, username, role FROM users WHERE username = 'tu_usuario';
```

### Error: "Contraseña actual incorrecta"
**Causa:** La contraseña proporcionada no coincide  
**Solución:** Verificar que estés usando la contraseña correcta actual

### Error: tabla password_audit_logs no existe
**Causa:** No se ejecutó la migración  
**Solución:** Ejecutar la migración SQL (ver sección "Migración de Base de Datos")

### Error: "No se pudieron validar las credenciales"
**Causa:** Token JWT inválido o expirado  
**Solución:** Hacer login nuevamente para obtener un token nuevo

## 📝 Notas Adicionales

### Recomendaciones de Producción

1. **Rate Limiting**
   - Implementar límite de intentos (ej: 5 por hora)
   - Usar `slowapi` o similar

2. **Notificaciones**
   - Enviar email cuando se cambie contraseña
   - Alertar al usuario de cambios no autorizados

3. **Invalidar Tokens**
   - Cerrar todas las sesiones después de cambio de contraseña
   - Forzar nuevo login

4. **Políticas de Contraseña Más Estrictas**
   - Requerir mayúsculas, minúsculas, números, símbolos
   - Historial de contraseñas (no reutilizar últimas 5)
   - Expiración periódica (cada 90 días)

5. **2FA para Admins**
   - Requerir segundo factor para operaciones sensibles

### Documentación Adicional

Para más detalles, ver:
- 📄 [docs/password-management.md](../docs/password-management.md) - Documentación completa
- 📄 [backend/migrations/001_add_password_audit_logs.sql](migrations/001_add_password_audit_logs.sql) - Script de migración

## ✅ Checklist de Implementación

- [x] Schemas creados (`ResetPasswordRequest`, `PasswordChangeResponse`)
- [x] Modelo de auditoría (`PasswordAuditLog`)
- [x] Endpoint de cambio de contraseña
- [x] Endpoint de reset por admin
- [x] Validación de permisos
- [x] Logs de auditoría
- [x] Hashing con bcrypt
- [x] Documentación completa
- [x] Scripts de migración
- [ ] Ejecutar migración en BD
- [ ] Testing manual
- [ ] Testing automatizado
- [ ] Rate limiting
- [ ] Notificaciones por email

## 📞 Contacto y Soporte

Para preguntas o problemas, contactar al equipo de desarrollo.

---

**Fecha de Implementación:** 2026-02-01  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para testing
