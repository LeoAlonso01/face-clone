# Gestión de Contraseñas - API Documentation

## Descripción General

Este documento describe los endpoints para cambio y reseteo de contraseñas en el sistema.

## Endpoints

### 1. Cambio de Contraseña (Usuario)

**Endpoint:** `POST /users/{user_id}/change_password`

**Autenticación:** Bearer token del usuario

**Permisos:**
- Los usuarios pueden cambiar su propia contraseña
- Los administradores pueden cambiar la contraseña de cualquier usuario

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Validaciones:**
- `current_password`: Debe coincidir con la contraseña actual del usuario
- `new_password`: 
  - Mínimo 8 caracteres
  - No puede ser igual a la contraseña actual

**Response Exitoso (200):**
```json
{
  "message": "Contraseña actualizada exitosamente",
  "success": true
}
```

**Errores Posibles:**

- **400 Bad Request:** 
  - Contraseña actual incorrecta
  - Nueva contraseña no cumple con requisitos
  - Nueva contraseña igual a la actual
  
- **403 Forbidden:** 
  - Usuario intenta cambiar contraseña de otro usuario sin ser admin
  
- **404 Not Found:** 
  - Usuario no encontrado

**Ejemplo con cURL:**
```bash
# Usuario cambiando su propia contraseña
curl -X POST "http://localhost:8000/users/123/change_password" \
  -H "Authorization: Bearer <user_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "oldPassword123",
    "new_password": "newStrongPassword123!"
  }'

# Admin cambiando contraseña de otro usuario
curl -X POST "http://localhost:8000/users/456/change_password" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "oldPassword123",
    "new_password": "newStrongPassword123!"
  }'
```

---

### 2. Reseteo de Contraseña (Admin)

**Endpoint:** `POST /admin/users/{user_id}/reset_password`

**Autenticación:** Bearer token con rol ADMIN

**Permisos:**
- Solo administradores

**Request Body:**
```json
{
  "new_password": "string"
}
```

**Validaciones:**
- `new_password`: Mínimo 8 caracteres

**Response Exitoso (200):**
```json
{
  "message": "Contraseña reseteada exitosamente para el usuario <username>",
  "success": true
}
```

**Errores Posibles:**

- **400 Bad Request:** 
  - Nueva contraseña no cumple con requisitos mínimos
  
- **403 Forbidden:** 
  - Usuario no tiene rol de administrador
  
- **404 Not Found:** 
  - Usuario no encontrado

**Ejemplo con cURL:**
```bash
# Admin reseteando contraseña de un usuario
curl -X POST "http://localhost:8000/admin/users/123/reset_password" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "new_password": "user123"
  }'
```

---

## Seguridad Implementada

### 1. Hashing de Contraseñas
- **Algoritmo:** bcrypt
- **Cost factor:** 12 (por defecto en passlib)
- **Salt:** Generado automáticamente por bcrypt

### 2. Validación de Permisos
- Verificación de identidad del usuario (JWT)
- Validación de rol ADMIN para reseteo
- Prevención de cambios no autorizados

### 3. Auditoría
- Todos los cambios de contraseña por admin se registran en la tabla `password_audit_logs`
- Información registrada:
  - `admin_id`: ID del administrador que realizó el cambio
  - `target_user_id`: ID del usuario afectado
  - `action`: Tipo de acción (password_change, password_reset)
  - `timestamp`: Fecha y hora del cambio
  - `success`: Estado de la operación

### 4. Rate Limiting
⚠️ **PENDIENTE DE IMPLEMENTACIÓN**
- Se recomienda agregar rate limiting con middlewares como `slowapi`
- Límite sugerido: 5 intentos por hora por IP

### 5. Validación de Contraseñas
- Longitud mínima: 8 caracteres
- Se puede extender con requisitos adicionales:
  - Letras mayúsculas y minúsculas
  - Números
  - Caracteres especiales

---

## Políticas de Seguridad

### Mejores Prácticas Implementadas

✅ **Nunca se almacenan contraseñas en texto plano**
✅ **Las contraseñas hasheadas no se devuelven en las respuestas**
✅ **Logs de auditoría para acciones administrativas**
✅ **Validación de contraseña actual antes de cambiar**
✅ **Verificación de permisos en cada operación**

### Recomendaciones Adicionales

🔹 **Invalidar tokens JWT** después de cambio de contraseña
🔹 **Forzar cambio de contraseña** en el próximo login después de reset
🔹 **Notificación por email** cuando se cambie la contraseña
🔹 **Implementar 2FA** para administradores
🔹 **Historial de contraseñas** para prevenir reutilización

---

## Integración con Frontend

### Headers Requeridos
```javascript
{
  'Authorization': 'Bearer <token>',
  'Content-Type': 'application/json'
}
```

### Ejemplo JavaScript (Fetch API)

```javascript
// Cambiar contraseña (usuario)
async function changePassword(userId, currentPassword, newPassword) {
  const response = await fetch(`/users/${userId}/change_password`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      current_password: currentPassword,
      new_password: newPassword
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}

// Resetear contraseña (admin)
async function resetPassword(userId, newPassword) {
  const response = await fetch(`/admin/users/${userId}/reset_password`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${localStorage.getItem('token')}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      new_password: newPassword
    })
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail);
  }
  
  return await response.json();
}
```

### Ejemplo React

```jsx
import { useState } from 'react';

function ChangePasswordForm({ userId }) {
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess(false);

    try {
      const response = await fetch(`/users/${userId}/change_password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: currentPassword,
          new_password: newPassword
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail);
      }

      const data = await response.json();
      setSuccess(true);
      setCurrentPassword('');
      setNewPassword('');
      
      // Opcional: Cerrar sesión y redirigir al login
      // localStorage.removeItem('token');
      // navigate('/login');
      
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Contraseña Actual:</label>
        <input
          type="password"
          value={currentPassword}
          onChange={(e) => setCurrentPassword(e.target.value)}
          required
        />
      </div>
      
      <div>
        <label>Nueva Contraseña:</label>
        <input
          type="password"
          value={newPassword}
          onChange={(e) => setNewPassword(e.target.value)}
          required
          minLength={8}
        />
      </div>
      
      {error && <div className="error">{error}</div>}
      {success && <div className="success">Contraseña actualizada exitosamente</div>}
      
      <button type="submit">Cambiar Contraseña</button>
    </form>
  );
}
```

---

## Testing

### Casos de Prueba Requeridos

#### 1. Cambio de Contraseña (Usuario)

**Caso exitoso:**
- ✅ Usuario cambia su propia contraseña correctamente
- ✅ Admin cambia contraseña de otro usuario

**Casos de error:**
- ❌ Contraseña actual incorrecta
- ❌ Nueva contraseña muy corta (< 8 caracteres)
- ❌ Nueva contraseña igual a la actual
- ❌ Usuario intenta cambiar contraseña de otro usuario (sin ser admin)
- ❌ Usuario no autenticado

#### 2. Reseteo de Contraseña (Admin)

**Caso exitoso:**
- ✅ Admin resetea contraseña de usuario
- ✅ Se registra log de auditoría

**Casos de error:**
- ❌ Usuario sin rol admin intenta resetear contraseña
- ❌ Nueva contraseña muy corta
- ❌ Usuario objetivo no existe
- ❌ Sin token de autenticación

### Ejemplo de Tests (pytest)

```python
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_change_password_success(user_token, user_id):
    """Test exitoso de cambio de contraseña"""
    response = client.post(
        f"/users/{user_id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "oldPassword123",
            "new_password": "newPassword456!"
        }
    )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_change_password_wrong_current(user_token, user_id):
    """Test con contraseña actual incorrecta"""
    response = client.post(
        f"/users/{user_id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "wrongPassword",
            "new_password": "newPassword456!"
        }
    )
    assert response.status_code == 400
    assert "incorrecta" in response.json()["detail"]

def test_reset_password_admin_success(admin_token, user_id):
    """Test exitoso de reseteo de contraseña por admin"""
    response = client.post(
        f"/admin/users/{user_id}/reset_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "user123"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True

def test_reset_password_non_admin_forbidden(user_token, user_id):
    """Test de reseteo por usuario no-admin (debe fallar)"""
    response = client.post(
        f"/admin/users/{user_id}/reset_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"new_password": "user123"}
    )
    assert response.status_code == 403
```

---

## Base de Datos

### Modelo de Auditoría

```sql
CREATE TABLE password_audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL REFERENCES users(id),
    target_user_id INTEGER NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT NOW(),
    success BOOLEAN DEFAULT TRUE
);

-- Índices para consultas eficientes
CREATE INDEX idx_audit_admin ON password_audit_logs(admin_id);
CREATE INDEX idx_audit_target ON password_audit_logs(target_user_id);
CREATE INDEX idx_audit_timestamp ON password_audit_logs(timestamp);
```

### Consultas Útiles

```sql
-- Ver todos los cambios realizados por un admin
SELECT * FROM password_audit_logs 
WHERE admin_id = 1 
ORDER BY timestamp DESC;

-- Ver historial de cambios de un usuario
SELECT * FROM password_audit_logs 
WHERE target_user_id = 123 
ORDER BY timestamp DESC;

-- Actividad de reseteo en las últimas 24 horas
SELECT 
    u1.username as admin,
    u2.username as target_user,
    pal.action,
    pal.timestamp
FROM password_audit_logs pal
JOIN users u1 ON pal.admin_id = u1.id
JOIN users u2 ON pal.target_user_id = u2.id
WHERE pal.timestamp > NOW() - INTERVAL '24 hours'
ORDER BY pal.timestamp DESC;
```

---

## Migración de Base de Datos

### Crear migración con Alembic

```bash
# En el directorio backend/
cd backend

# Generar migración
alembic revision --autogenerate -m "Add password audit logs table"

# Aplicar migración
alembic upgrade head
```

### Migración Manual (si es necesario)

```sql
-- Crear tabla de logs de auditoría
CREATE TABLE password_audit_logs (
    id SERIAL PRIMARY KEY,
    admin_id INTEGER NOT NULL,
    target_user_id INTEGER NOT NULL,
    action VARCHAR(50) NOT NULL,
    ip_address VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    success BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (admin_id) REFERENCES users(id),
    FOREIGN KEY (target_user_id) REFERENCES users(id)
);

-- Crear índices
CREATE INDEX idx_password_audit_admin_id ON password_audit_logs(admin_id);
CREATE INDEX idx_password_audit_target_user_id ON password_audit_logs(target_user_id);
CREATE INDEX idx_password_audit_timestamp ON password_audit_logs(timestamp);
```

---

## Troubleshooting

### Error: "Solo los administradores pueden realizar esta acción"
**Causa:** El token no tiene rol ADMIN  
**Solución:** Verificar que el usuario tenga rol ADMIN en la base de datos

### Error: "Contraseña actual incorrecta"
**Causa:** La contraseña proporcionada no coincide con la almacenada  
**Solución:** Verificar que el usuario esté ingresando su contraseña actual correcta

### Error: "La nueva contraseña debe tener al menos 8 caracteres"
**Causa:** Validación de seguridad  
**Solución:** Usar una contraseña más larga

---

## Changelog

### v1.0.0 (2026-02-01)
- ✅ Implementación inicial de endpoints
- ✅ Validación de contraseñas
- ✅ Logs de auditoría
- ✅ Documentación completa

### Pendiente
- ⏳ Rate limiting
- ⏳ Notificaciones por email
- ⏳ Invalidación de tokens JWT después de cambio
- ⏳ 2FA para administradores
