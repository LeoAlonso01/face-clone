# 🔐 Autenticación y Gestión de Usuarios

## 📋 Endpoints de Autenticación

### 1. Obtener Token de Acceso

**Endpoint**: `POST /token`

Obtiene un token JWT para autenticación en endpoints protegidos.

**Parámetros** (form-data):
- `username` (string, requerido): Nombre de usuario
- `password` (string, requerido): Contraseña

**Respuesta**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Ejemplo cURL**:
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=tu_password"
```

### 2. Registrar Nuevo Usuario

**Endpoint**: `POST /register`

Crea un nuevo usuario en el sistema (solo administradores).

**Body** (JSON):
```json
{
  "username": "nuevo_usuario",
  "email": "usuario@ejemplo.com",
  "password": "contraseña_segura",
  "role": "USER"
}
```

**Roles disponibles**: `USER`, `ADMIN`, `AUDITOR`

**Headers requeridos**:
- `Authorization: Bearer <token_admin>`

### 3. Listar Usuarios

**Endpoint**: `GET /users`

Obtiene lista paginada de usuarios.

**Query Parameters**:
- `skip` (int, opcional): Número de registros a saltar (default: 0)
- `limit` (int, opcional): Límite de registros (default: 100)

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 4. Obtener Usuario Específico

**Endpoint**: `GET /users/{user_id}`

Obtiene información detallada de un usuario.

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 5. Eliminar Usuario (Soft Delete)

**Endpoint**: `DELETE /users/{user_id}`

Marca un usuario como eliminado (soft delete).

**Headers requeridos**:
- `Authorization: Bearer <token_admin>`

### 6. Cambiar Contraseña

**Endpoint**: `PUT /users/{user_id}/change-password`

Cambia la contraseña de un usuario.

**Body** (JSON):
```json
{
  "current_password": "contraseña_actual",
  "new_password": "nueva_contraseña"
}
```

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 7. Recuperación de Contraseña

**Endpoint**: `POST /forgot-password`

Inicia proceso de recuperación de contraseña.

**Body** (JSON):
```json
{
  "email": "usuario@ejemplo.com"
}
```

## 🔐 Middleware de Autenticación

### Función `get_current_user`

Valida tokens JWT y obtiene el usuario autenticado con sus relaciones cargadas.

**Ubicación**: [auth.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/auth.py#L43-L67)

**Características**:
- Valida token JWT con clave secreta
- Carga relación con unidad responsable usando `joinedload`
- Maneja excepciones de credenciales inválidas

### Función `get_admin_user`

Valida que el usuario actual tenga rol de administrador.

**Ubicación**: [auth.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/auth.py#L69-L75)

## 🛡️ Configuración de Seguridad

**Ubicación**: [auth.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/auth.py#L14-L19)

```python
SECRET_KEY = "tu_clave_secreta"  # Cambiar en producción
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
```

## 📝 Ejemplos de Uso

### Autenticación en Frontend

```javascript
// Login
const response = await fetch('/token', {
  method: 'POST',
  headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  body: `username=${username}&password=${password}`
});

const { access_token } = await response.json();

// Requests autenticados
const usersResponse = await fetch('/users', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### Headers de Autorización

```bash
# Ejemplo con curl
curl -H "Authorization: Bearer TU_TOKEN_JWT" \
  "http://localhost:8000/users"
```

## ⚠️ Consideraciones de Seguridad

1. **Tokens JWT**: Los tokens expiran después de 30 minutos
2. **Clave Secreta**: Debe ser cambiada en entorno de producción
3. **HTRECOMENDADO**: Usar HTTPS en producción
4. **Validación de Roles**: Endpoints sensibles requieren rol ADMIN

## 🔄 Flujo de Autenticación

1. Usuario envía credenciales a `/token`
2. Servidor valida y retorna JWT
3. Cliente incluye JWT en header `Authorization`
4. Servidor valida JWT en cada request protegido
5. Si el token expira, cliente debe reautenticarse

---
*Documentación actualizada: Enero 2026*