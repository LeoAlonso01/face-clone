# 🏢 Gestión de Unidades Responsables

## 📋 Endpoints Principales

### 1. Listar Unidades Responsables

**Endpoint**: `GET /unidades_responsables`

Obtiene todas las unidades responsables con paginación.

**Query Parameters**:
- `skip` (int, opcional): Registros a saltar (default: 0)
- `limit` (int, opcional): Límite de resultados (default: 100)
- `search` (string, opcional): Búsqueda por nombre

**Headers requeridos**:
- `Authorization: Bearer <token>`

**Respuesta**: Lista de objetos `UnidadResponsableResponse`

### 2. Obtener Unidad Específica

**Endpoint**: `GET /unidades_responsables/{id_unidad}`

Obtiene información detallada de una unidad específica.

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 3. Actualizar Unidad Responsable

**Endpoint**: `PUT /unidades_responsables/{id_unidad}`

Actualiza información de una unidad responsable, incluyendo asignación de responsable.

**Body** (JSON) - **Campos opcionales**:
```json
{
  "nombre": "Nuevo nombre",
  "telefono": "1234567890",
  "domicilio": "Nueva dirección",
  "responsable_id": 4,
  "tipo_unidad": "Nuevo tipo"
}
```

**Formato alternativo**:
```json
{
  "responsable": {
    "id": 4
  }
}
```

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 4. Obtener Unidad por Usuario

**Endpoint**: `GET /unidad_por_usuario/{user_id}`

Obtiene la unidad responsable asignada a un usuario específico.

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 5. Estructura Jerárquica

**Endpoint**: `GET /debug/unidad-estructura`

Obtiene la estructura jerárquica completa de unidades (debug).

**Headers requeridos**:
- `Authorization: Bearer <token>`

## 🏗️ Estructura de Datos

### Modelo UnidadResponsable

**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L74-L109)

**Campos principales**:
- `id_unidad` (Integer, PK): Identificador único
- `nombre` (String, requerido): Nombre de la unidad
- `responsable` (Integer, FK): ID del usuario responsable
- `tipo_unidad` (String): Tipo de unidad
- `unidad_padre_id` (Integer, FK): ID de unidad padre (jerarquía)
- `fecha_creacion` (DateTime): Fecha de creación
- `fecha_cambio` (DateTime): Última actualización

### Relaciones

- **Usuario Responsable**: Relación 1:1 con modelo User
- **Unidades Dependientes**: Relación jerárquica consigo misma
- **Actas**: Relación 1:N con Actas de Entrega-Recepción

## 📊 Esquemas Pydantic

### UnidadResponsableBase

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L91-L114)

Campos base con validaciones para creación y actualización.

### UnidadResponsableUpdate

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L119-L134)

**Características**:
- Todos los campos son opcionales
- Soporta actualizaciones parciales
- Permite asignar responsable por ID o objeto

### UnidadResponsableResponse

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L138-L159)

Incluye información del usuario responsable embebida.

## 🎯 Ejemplos de Uso

### Asignar Responsable a Unidad

```bash
curl -X PUT "http://localhost:8000/unidades_responsables/301" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"responsable_id": 4}'
```

### Obtener Todas las Unidades

```bash
curl -H "Authorization: Bearer TU_TOKEN" \
  "http://localhost:8000/unidades_responsables?limit=50"
```

### Buscar Unidades por Nombre

```bash
curl -H "Authorization: Bearer TU_TOKEN" \
  "http://localhost:8000/unidades_responsables?search=contraloria"
```

## ⚙️ Configuración del Endpoint

**Ubicación**: [main.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/main.py#L620-L666)

**Características del endpoint PUT**:
- Valida permisos de usuario
- Soporta ambos formatos de responsable
- Actualiza timestamp de modificación
- Retorna la unidad actualizada con responsable embebido

## 🛡️ Validaciones y Seguridad

1. **Autenticación requerida** en todos los endpoints
2. **Validación de datos** con esquemas Pydantic
3. **Campos opcionales** en actualizaciones parciales
4. **Manejo de errores** con códigos HTTP apropiados

## 🔄 Flujo de Asignación de Responsable

1. Frontend obtiene lista de unidades y usuarios
2. Usuario selecciona unidad y responsable
3. Se envía PUT con `responsable_id`
4. Backend actualiza la relación
5. Frontend recibe respuesta con datos actualizados
6. Se refresca la interfaz con el nuevo responsable

---
*Documentación actualizada: Enero 2026*