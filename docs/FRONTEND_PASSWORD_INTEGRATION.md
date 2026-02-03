# Instrucciones para Agente Frontend - Integración de Cambio de Contraseña

## 🎯 Objetivo
Implementar la interfaz de usuario para los endpoints de gestión de contraseñas que ya están funcionando en el backend.

## 📡 Endpoints Disponibles del Backend

### 1. Cambio de Contraseña (Usuario)
```
POST http://localhost:8000/users/{user_id}/change_password
```

**Headers requeridos:**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Validaciones:**
- `current_password`: requerido, debe coincidir con la contraseña actual
- `new_password`: requerido, mínimo 8 caracteres

**Respuestas:**

✅ **Éxito (200):**
```json
{
  "message": "Contraseña actualizada exitosamente",
  "success": true
}
```

❌ **Errores:**
- `400` - Contraseña actual incorrecta o nueva contraseña inválida
- `401` - No autenticado
- `403` - Sin permisos (intentando cambiar contraseña de otro usuario)
- `404` - Usuario no encontrado
- `422` - Error de validación (contraseña muy corta)

---

### 2. Reset de Contraseña (Solo Admin)
```
POST http://localhost:8000/admin/users/{user_id}/reset_password
```

**Headers requeridos:**
```
Authorization: Bearer <admin_token>
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "new_password": "string"
}
```

**Validaciones:**
- `new_password`: requerido, mínimo 8 caracteres
- El usuario debe tener rol ADMIN

**Respuestas:**

✅ **Éxito (200):**
```json
{
  "message": "Contraseña reseteada exitosamente para el usuario {username}",
  "success": true
}
```

❌ **Errores:**
- `403` - Usuario no es administrador
- `404` - Usuario objetivo no encontrado
- `422` - Nueva contraseña muy corta

---

## 🛠️ Componentes a Implementar

### Componente 1: Formulario de Cambio de Contraseña (Usuario)

**Ubicación sugerida:** `src/components/ChangePasswordForm.jsx` o similar

**Props requeridos:**
- `userId`: ID del usuario actual (obtenido del contexto/estado de autenticación)
- `token`: JWT token del usuario autenticado

**Campos del formulario:**
```jsx
1. currentPassword (input type="password")
   - Label: "Contraseña Actual"
   - Required: true
   - Placeholder: "Ingresa tu contraseña actual"

2. newPassword (input type="password")
   - Label: "Nueva Contraseña"
   - Required: true
   - MinLength: 8
   - Placeholder: "Mínimo 8 caracteres"

3. confirmPassword (input type="password")
   - Label: "Confirmar Nueva Contraseña"
   - Required: true
   - Validación: debe coincidir con newPassword
   - Placeholder: "Repite la nueva contraseña"
```

**Ejemplo de código React:**

```jsx
import { useState } from 'react';

export default function ChangePasswordForm({ userId, token }) {
  const [formData, setFormData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError(''); // Limpiar errores al escribir
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validación local
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (formData.newPassword.length < 8) {
      setError('La nueva contraseña debe tener al menos 8 caracteres');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`http://localhost:8000/users/${userId}/change_password`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: formData.currentPassword,
          new_password: formData.newPassword
        })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al cambiar contraseña');
      }

      setSuccess(data.message);
      
      // Limpiar formulario
      setFormData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });

      // Opcional: Cerrar sesión y redirigir al login
      // setTimeout(() => {
      //   logout();
      //   navigate('/login');
      // }, 2000);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold">Cambiar Contraseña</h2>

      {/* Contraseña Actual */}
      <div>
        <label htmlFor="currentPassword" className="block mb-2">
          Contraseña Actual *
        </label>
        <input
          type="password"
          id="currentPassword"
          name="currentPassword"
          value={formData.currentPassword}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded"
          placeholder="Ingresa tu contraseña actual"
        />
      </div>

      {/* Nueva Contraseña */}
      <div>
        <label htmlFor="newPassword" className="block mb-2">
          Nueva Contraseña *
        </label>
        <input
          type="password"
          id="newPassword"
          name="newPassword"
          value={formData.newPassword}
          onChange={handleChange}
          required
          minLength={8}
          className="w-full px-3 py-2 border rounded"
          placeholder="Mínimo 8 caracteres"
        />
      </div>

      {/* Confirmar Contraseña */}
      <div>
        <label htmlFor="confirmPassword" className="block mb-2">
          Confirmar Nueva Contraseña *
        </label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          className="w-full px-3 py-2 border rounded"
          placeholder="Repite la nueva contraseña"
        />
      </div>

      {/* Mensajes de Error/Éxito */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      {/* Botón de Envío */}
      <button
        type="submit"
        disabled={loading}
        className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? 'Cambiando...' : 'Cambiar Contraseña'}
      </button>
    </form>
  );
}
```

---

### Componente 2: Formulario de Reset de Contraseña (Admin)

**Ubicación sugerida:** `src/components/AdminResetPasswordForm.jsx` o similar

**Props requeridos:**
- `targetUserId`: ID del usuario cuya contraseña se va a resetear
- `targetUsername`: Nombre del usuario (para mostrar confirmación)
- `adminToken`: JWT token del administrador

**Campos del formulario:**
```jsx
1. newPassword (input type="password")
   - Label: "Nueva Contraseña para {username}"
   - Required: true
   - MinLength: 8
   - Placeholder: "Mínimo 8 caracteres"

2. confirmPassword (input type="password")
   - Label: "Confirmar Contraseña"
   - Required: true
   - Validación: debe coincidir con newPassword
```

**Ejemplo de código React:**

```jsx
import { useState } from 'react';

export default function AdminResetPasswordForm({ targetUserId, targetUsername, adminToken, onSuccess }) {
  const [formData, setFormData] = useState({
    newPassword: '',
    confirmPassword: ''
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Mostrar confirmación primero
    if (!showConfirmation) {
      setShowConfirmation(true);
      return;
    }

    setError('');
    setSuccess('');

    // Validación local
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return;
    }

    if (formData.newPassword.length < 8) {
      setError('La contraseña debe tener al menos 8 caracteres');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(
        `http://localhost:8000/admin/users/${targetUserId}/reset_password`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${adminToken}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            new_password: formData.newPassword
          })
        }
      );

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Error al resetear contraseña');
      }

      setSuccess(data.message);
      
      // Limpiar formulario
      setFormData({
        newPassword: '',
        confirmPassword: ''
      });
      setShowConfirmation(false);

      // Callback opcional
      if (onSuccess) {
        setTimeout(() => onSuccess(), 2000);
      }

    } catch (err) {
      setError(err.message);
      setShowConfirmation(false);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    setShowConfirmation(false);
    setError('');
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <h2 className="text-2xl font-bold text-red-600">
        Resetear Contraseña
      </h2>

      <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
        <strong>Atención:</strong> Vas a resetear la contraseña del usuario <strong>{targetUsername}</strong>
      </div>

      {/* Nueva Contraseña */}
      <div>
        <label htmlFor="newPassword" className="block mb-2">
          Nueva Contraseña *
        </label>
        <input
          type="password"
          id="newPassword"
          name="newPassword"
          value={formData.newPassword}
          onChange={handleChange}
          required
          minLength={8}
          disabled={showConfirmation}
          className="w-full px-3 py-2 border rounded disabled:bg-gray-200"
          placeholder="Mínimo 8 caracteres"
        />
      </div>

      {/* Confirmar Contraseña */}
      <div>
        <label htmlFor="confirmPassword" className="block mb-2">
          Confirmar Contraseña *
        </label>
        <input
          type="password"
          id="confirmPassword"
          name="confirmPassword"
          value={formData.confirmPassword}
          onChange={handleChange}
          required
          disabled={showConfirmation}
          className="w-full px-3 py-2 border rounded disabled:bg-gray-200"
          placeholder="Repite la contraseña"
        />
      </div>

      {/* Confirmación */}
      {showConfirmation && (
        <div className="bg-orange-100 border border-orange-400 text-orange-700 px-4 py-3 rounded">
          <p className="font-bold">¿Estás seguro?</p>
          <p>Esta acción reseteará la contraseña de {targetUsername}</p>
        </div>
      )}

      {/* Mensajes */}
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded">
          {success}
        </div>
      )}

      {/* Botones */}
      <div className="flex gap-2">
        {!showConfirmation ? (
          <button
            type="submit"
            disabled={loading}
            className="flex-1 bg-red-500 text-white py-2 px-4 rounded hover:bg-red-600 disabled:bg-gray-400"
          >
            Resetear Contraseña
          </button>
        ) : (
          <>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-red-600 text-white py-2 px-4 rounded hover:bg-red-700"
            >
              {loading ? 'Reseteando...' : 'Confirmar Reset'}
            </button>
            <button
              type="button"
              onClick={handleCancel}
              disabled={loading}
              className="flex-1 bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600"
            >
              Cancelar
            </button>
          </>
        )}
      </div>
    </form>
  );
}
```

---

## 🔗 Integración con Contexto de Autenticación

**Asume que ya tienes un contexto de autenticación que proporciona:**
- `user` (objeto con `id`, `username`, `role`, etc.)
- `token` (JWT token)

### Ejemplo de uso en un componente de perfil:

```jsx
import { useAuth } from '@/context/AuthContext';
import ChangePasswordForm from '@/components/ChangePasswordForm';

export default function ProfilePage() {
  const { user, token } = useAuth();

  return (
    <div className="max-w-2xl mx-auto p-6">
      <h1>Mi Perfil</h1>
      
      {/* Otros datos del perfil */}
      
      {/* Formulario de cambio de contraseña */}
      <div className="mt-8">
        <ChangePasswordForm 
          userId={user.id} 
          token={token} 
        />
      </div>
    </div>
  );
}
```

### Ejemplo de uso en panel de admin:

```jsx
import { useAuth } from '@/context/AuthContext';
import AdminResetPasswordForm from '@/components/AdminResetPasswordForm';
import { useState } from 'react';

export default function AdminUserManagement() {
  const { token } = useAuth();
  const [selectedUser, setSelectedUser] = useState(null);

  // Función para seleccionar usuario de una lista
  const handleSelectUser = (user) => {
    setSelectedUser(user);
  };

  return (
    <div className="grid grid-cols-2 gap-6">
      {/* Lista de usuarios */}
      <div>
        <h2>Usuarios</h2>
        {/* Aquí va tu lista de usuarios */}
      </div>

      {/* Formulario de reset */}
      <div>
        {selectedUser && (
          <AdminResetPasswordForm
            targetUserId={selectedUser.id}
            targetUsername={selectedUser.username}
            adminToken={token}
            onSuccess={() => setSelectedUser(null)}
          />
        )}
      </div>
    </div>
  );
}
```

---

## 🎨 Variantes de Framework

### Vue.js (Composition API)

```vue
<script setup>
import { ref } from 'vue';

const props = defineProps({
  userId: Number,
  token: String
});

const formData = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
});

const error = ref('');
const success = ref('');
const loading = ref(false);

const handleSubmit = async () => {
  error.value = '';
  success.value = '';

  if (formData.value.newPassword !== formData.value.confirmPassword) {
    error.value = 'Las contraseñas no coinciden';
    return;
  }

  loading.value = true;

  try {
    const response = await fetch(
      `http://localhost:8000/users/${props.userId}/change_password`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${props.token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          current_password: formData.value.currentPassword,
          new_password: formData.value.newPassword
        })
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail);
    }

    success.value = data.message;
    formData.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    };
  } catch (err) {
    error.value = err.message;
  } finally {
    loading.value = false;
  }
};
</script>

<template>
  <form @submit.prevent="handleSubmit">
    <!-- Campos del formulario -->
  </form>
</template>
```

### Angular

```typescript
import { Component, Input } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-change-password',
  template: `<!-- template aquí -->`
})
export class ChangePasswordComponent {
  @Input() userId!: number;
  @Input() token!: string;

  formData = {
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  };

  error = '';
  success = '';
  loading = false;

  constructor(private http: HttpClient) {}

  handleSubmit() {
    this.error = '';
    this.success = '';

    if (this.formData.newPassword !== this.formData.confirmPassword) {
      this.error = 'Las contraseñas no coinciden';
      return;
    }

    this.loading = true;

    const headers = new HttpHeaders({
      'Authorization': `Bearer ${this.token}`,
      'Content-Type': 'application/json'
    });

    this.http.post(
      `http://localhost:8000/users/${this.userId}/change_password`,
      {
        current_password: this.formData.currentPassword,
        new_password: this.formData.newPassword
      },
      { headers }
    ).subscribe({
      next: (response: any) => {
        this.success = response.message;
        this.formData = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        };
        this.loading = false;
      },
      error: (err) => {
        this.error = err.error.detail || 'Error al cambiar contraseña';
        this.loading = false;
      }
    });
  }
}
```

---

## 🧪 Datos de Prueba

**Usuario para pruebas:**
```
Username: Leo Alonso
Password: user12345
Role: USER
ID: 4
```

**Admin para pruebas:**
```
Username: Dani Alonso
Password: admin123
Role: ADMIN
ID: 1
```

**Backend URL:**
```
http://localhost:8000
```

---

## ✅ Checklist de Implementación

### Formulario de Cambio de Contraseña (Usuario)
- [ ] Crear componente `ChangePasswordForm`
- [ ] Agregar 3 campos: currentPassword, newPassword, confirmPassword
- [ ] Validar que newPassword y confirmPassword coincidan
- [ ] Validar longitud mínima de 8 caracteres
- [ ] Enviar POST a `/users/{id}/change_password`
- [ ] Incluir header `Authorization: Bearer {token}`
- [ ] Manejar respuestas 200, 400, 401, 403, 404
- [ ] Mostrar mensaje de éxito/error
- [ ] Limpiar formulario después de éxito
- [ ] (Opcional) Cerrar sesión después de cambiar contraseña

### Formulario de Reset (Admin)
- [ ] Crear componente `AdminResetPasswordForm`
- [ ] Agregar 2 campos: newPassword, confirmPassword
- [ ] Mostrar nombre del usuario objetivo
- [ ] Agregar confirmación antes de resetear
- [ ] Validar longitud mínima de 8 caracteres
- [ ] Enviar POST a `/admin/users/{id}/reset_password`
- [ ] Incluir header `Authorization: Bearer {admin_token}`
- [ ] Verificar que el usuario tiene rol ADMIN
- [ ] Manejar respuestas 200, 403, 404, 422
- [ ] Mostrar mensaje de éxito/error

### Integración
- [ ] Obtener `userId` y `token` del contexto de auth
- [ ] Agregar formulario de cambio en página de perfil/settings
- [ ] Agregar formulario de reset en panel de admin
- [ ] Probar flujo completo de cambio de contraseña
- [ ] Probar flujo completo de reset (solo admin)
- [ ] Verificar manejo de errores

---

## 🐛 Errores Comunes y Soluciones

### Error: "No tienes permisos para cambiar la contraseña de otro usuario"
**Causa:** Usuario intenta cambiar contraseña de otro usuario sin ser admin  
**Solución:** Verificar que `userId` coincida con el usuario autenticado

### Error: "Contraseña actual incorrecta"
**Causa:** El campo `current_password` no coincide con la contraseña en BD  
**Solución:** Verificar que el usuario ingrese su contraseña actual correcta

### Error: "La contraseña debe tener al menos 8 caracteres"
**Causa:** Validación de backend rechaza contraseñas cortas  
**Solución:** Agregar validación en frontend antes de enviar

### Error: "Solo los administradores pueden realizar esta acción"
**Causa:** Usuario no-admin intenta usar el endpoint de reset  
**Solución:** Verificar rol antes de mostrar el formulario de reset

### Error: CORS
**Causa:** Frontend y backend en diferentes dominios  
**Solución:** Backend ya tiene CORS configurado, verificar que el frontend use `http://localhost:8000`

---

## 📚 Recursos Adicionales

- **Documentación completa:** Ver `/docs/password-management.md`
- **Tests del backend:** Ver `/backend/tests/test_password_management.py`
- **Migración SQL:** Ver `/backend/migrations/001_add_password_audit_logs.sql`

---

## 🚀 Siguiente Paso

1. **Crear los componentes** en tu proyecto frontend
2. **Probar el flujo completo** con los usuarios de prueba
3. **Ajustar estilos** según tu diseño
4. **Agregar validaciones adicionales** si es necesario (ej: requisitos de complejidad)
5. **Implementar notificaciones** (opcional: toast, modal, etc.)

¡Todo está listo en el backend! Solo necesitas construir los formularios en el frontend siguiendo estos ejemplos.
