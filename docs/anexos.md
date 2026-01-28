# 📎 Gestión de Anexos Documentales

## 📋 Endpoints Principales

### 1. Listar Anexos

**Endpoint**: `GET /anexos`

Obtiene todos los anexos documentales con paginación.

**Query Parameters**:
- `skip` (int, opcional): Registros a saltar (default: 0)
- `limit` (int, opcional): Límite de resultados (default: 100)

**Headers requeridos**:
- `Authorization: Bearer <token>`

**Respuesta**: Lista de objetos `AnexoResponse`

### 2. Obtener Anexo Específico

**Endpoint**: `GET /anexos/{anexo_id}`

Obtiene información detallada de un anexo específico.

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 3. Crear Nuevo Anexo

**Endpoint**: `POST /anexos`

Crea un nuevo anexo documental.

**Body** (JSON):
```json
{
  "clave": "ANEXO-001",
  "creador_id": 1,
  "datos": {
    "tipo": "contrato",
    "descripcion": "Contrato de servicios",
    "archivo": "contrato.pdf"
  },
  "estado": "ACTIVO",
  "unidad_responsable_id": 301,
  "acta_id": 123
}
```

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 4. Actualizar Anexo

**Endpoint**: `PUT /anexos/{anexo_id}`

Actualiza información de un anexo existente.

**Body** (JSON) - **Campos opcionales**:
```json
{
  "datos": {
    "descripcion": "Contrato actualizado"
  },
  "estado": "REVISADO"
}
```

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 5. Eliminar Anexo

**Endpoint**: `DELETE /anexos/{anexo_id}`

Elimina un anexo del sistema (soft delete).

**Headers requeridos**:
- `Authorization: Bearer <token_admin>` (solo administradores)

### 6. Buscar Anexos por Clave

**Endpoint**: `GET /anexos/clave/{clave}`

Busca anexos por clave específica.

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 7. Buscar Anexos por Estado

**Endpoint**: `GET /anexos/estado/{estado}`

Busca anexos por estado específico.

**Headers requeridos**:
- `Authorization: Bearer <token>`

## 🏗️ Estructura de Datos

### Modelo Anexos

**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L155-L174)

**Campos principales**:
- `id` (Integer, PK): Identificador único
- `clave` (String): Clave identificadora del anexo
- `creador_id` (Integer, FK): ID del usuario creador
- `datos` (JSON): Datos estructurados del anexo
- `estado` (String): Estado actual del anexo
- `unidad_responsable_id` (Integer, FK): ID de la unidad responsable
- `acta_id` (Integer, FK): ID del acta relacionada (opcional)
- `creado_en` (Date): Fecha de creación
- `actualizado_en` (Date): Última actualización
- `is_deleted` (Boolean): Soft delete flag

### Relaciones

- **Creador**: Relación con modelo User
- **Unidad Responsable**: Relación con modelo UnidadResponsable
- **Acta**: Relación opcional con modelo ActaEntregaRecepcion

## 📊 Esquemas Pydantic

### AnexoBase

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L183-L192)

Esquema base con campos comunes para anexos.

### AnexoCreate

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L193-L199)

Esquema para creación de nuevos anexos con validaciones.

### AnexoUpdate

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L200-L207)

Esquema para actualizaciones parciales de anexos (campos opcionales).

### AnexoResponse

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L208-L228)

Esquema de respuesta completo para anexos.

## 🎯 Ejemplos de Uso

### Crear Nuevo Anexo

```bash
curl -X POST "http://localhost:8000/anexos" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "clave": "CONTRATO-2024-001",
    "creador_id": 1,
    "datos": {
      "tipo": "contrato",
      "numero": "CT-001",
      "fecha_inicio": "2024-01-01",
      "fecha_fin": "2024-12-31",
      "monto": 50000,
      "archivos": ["contrato.pdf", "anexos.zip"]
    },
    "estado": "VIGENTE",
    "unidad_responsable_id": 301
  }'
```

### Listar Anexos por Estado

```bash
curl -H "Authorization: Bearer TU_TOKEN" \
  "http://localhost:8000/anexos/estado/VIGENTE"
```

### Buscar Anexos por Clave

```bash
curl -H "Authorization: Bearer TU_TOKEN" \
  "http://localhost:8000/anexos/clave/CONTRATO"
```

## ⚙️ Configuración del Endpoint

**Ubicación**: [main.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/main.py#L965-L1024)

**Características**:
- CRUD completo para anexos
- Búsqueda por clave y estado
- Validación de datos con esquemas Pydantic
- Manejo de relaciones con unidades y actas
- Soft delete implementation

## 🛡️ Validaciones y Seguridad

1. **Autenticación requerida** en todos los endpoints
2. **Validación de creador** existente
3. **Validación de unidad responsable** existente
4. **Validación de acta** existente (si se proporciona)
5. **Estructura JSON** validada para campo `datos`
6. **Permisos administrativos** para eliminación

## 📋 Estructura de Datos JSON

El campo `datos` puede contener cualquier estructura JSON, pero se recomienda:

```json
{
  "tipo": "tipo_documento",
  "descripcion": "Descripción del documento",
  "numero": "Número de referencia",
  "fechas": {
    "inicio": "2024-01-01",
    "fin": "2024-12-31"
  },
  "monto": 50000,
  "archivos": ["archivo1.pdf", "archivo2.zip"],
  "observaciones": "Notas adicionales"
}
```

## 🔄 Estados de Anexos

- **ACTIVO**: Anexo activo y vigente
- **VIGENTE**: Documento vigente
- **REVISADO**: Revisado y aprobado
- **ARCHIVADO**: Archivado para consulta
- **ELIMINADO**: Marcado para eliminación (soft delete)

## 📁 Relación con Actas

Los anexos pueden estar asociados a actas de entrega-recepción:

```json
{
  "acta_id": 123,
  "datos": {
    "tipo": "inventario",
    "descripcion": "Inventario de bienes entregados"
  }
}
```

---
*Documentación actualizada: Enero 2026*