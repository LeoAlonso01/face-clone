# 📋 Gestión de Actas de Entrega-Recepción

## 📋 Endpoints Principales

### 1. Listar Actas

**Endpoint**: `GET /actas`

Obtiene todas las actas de entrega-recepción con paginación.

**Query Parameters**:
- `skip` (int, opcional): Registros a saltar (default: 0)
- `limit` (int, opcional): Límite de resultados (default: 100)

**Headers requeridos**:
- `Authorization: Bearer <token>`

**Respuesta**: Lista de objetos `ActaResponse`

### 2. Obtener Acta Específica

**Endpoint**: `GET /actas/{acta_id}`

Obtiene información detallada de un acta específica.

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 3. Crear Nueva Acta

**Endpoint**: `POST /actas`

Crea una nueva acta de entrega-recepción.

**Body** (JSON):
```json
{
  "unidad_responsable": 301,
  "folio": "ACTA-2024-001",
  "fecha": "2024-01-15",
  "hora": "10:30:00",
  "comisionado": "Juan Pérez",
  "entrante": "María García",
  "saliente": "Carlos López"
}
```

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 4. Actualizar Acta

**Endpoint**: `PUT /actas/{acta_id}`

Actualiza información de un acta existente.

**Body** (JSON) - **Campos opcionales**:
```json
{
  "folio": "ACTA-2024-001-REV",
  "observaciones": "Acta revisada y corregida",
  "estado": "COMPLETADA"
}
```

**Headers requeridos**:
- `Authorization: Bearer <token>`

### 5. Eliminar Acta

**Endpoint**: `DELETE /actas/{acta_id}`

Elimina un acta del sistema.

**Headers requeridos**:
- `Authorization: Bearer <token_admin>` (solo administradores)

## 🏗️ Estructura de Datos

### Modelo ActaEntregaRecepcion

**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L112-L154)

**Campos principales**:
- `id` (Integer, PK): Identificador único
- `unidad_responsable` (Integer, FK): ID de la unidad responsable
- `folio` (String): Número de folio del acta
- `fecha` (String): Fecha del acta
- `hora` (String): Hora del acta
- `comisionado` (String): Nombre del comisionado
- `entrante` (String): Nombre del entrante
- `saliente` (String): Nombre del saliente
- `estado` (String): Estado del acta
- `creado_en` (DateTime): Fecha de creación
- `actualizado_en` (DateTime): Última actualización

### Relaciones

- **Unidad Responsable**: Relación con modelo UnidadResponsable
- **Anexos**: Relación 1:N con Anexos documentales

## 📊 Esquemas Pydantic

### ActaCreate

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L229-L257)

Esquema para creación de nuevas actas con validaciones.

### ActaResponse

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L258-L294)

Esquema de respuesta que incluye todos los campos del acta.

### ActaWithUnidadResponse

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L295-L301)

Extiende ActaResponse incluyendo información de la unidad responsable.

### ActaUpdate

**Ubicación**: [schemas.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/schemas.py#L302-L316)

Esquema para actualizaciones parciales de actas (todos los campos opcionales).

## 🎯 Ejemplos de Uso

### Crear Nueva Acta

```bash
curl -X POST "http://localhost:8000/actas" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "unidad_responsable": 301,
    "folio": "ACTA-2024-001",
    "fecha": "2024-01-15",
    "hora": "10:30:00",
    "comisionado": "Juan Pérez",
    "entrante": "María García",
    "saliente": "Carlos López"
  }'
```

### Listar Todas las Actas

```bash
curl -H "Authorization: Bearer TU_TOKEN" \
  "http://localhost:8000/actas?limit=20"
```

### Actualizar Acta

```bash
curl -X PUT "http://localhost:8000/actas/123" \
  -H "Authorization: Bearer TU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"observaciones": "Acta revisada", "estado": "FINALIZADA"}'
```

## ⚙️ Configuración del Endpoint

**Ubicación**: [main.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/main.py#L832-L948)

**Características**:
- CRUD completo para actas
- Validación de datos con esquemas Pydantic
- Manejo de relaciones con unidades y anexos
- Timestamps automáticos de creación y actualización

## 🛡️ Validaciones y Seguridad

1. **Autenticación requerida** en todos los endpoints
2. **Validación de unidad responsable** existente
3. **Campos requeridos** para creación
4. **Campos opcionales** para actualizaciones
5. **Permisos administrativos** para eliminación

## 📋 Campos del Acta

### Información Básica
- **Folio**: Identificador único del acta
- **Fecha y Hora**: Fecha y hora del acto
- **Comisionado**: Persona que comisiona el acta

### Partes Involucradas
- **Entrante**: Persona que recibe el cargo
- **Saliente**: Persona que entrega el cargo
- **Testigos**: Testigos de ambas partes (opcional)

### Información Adicional
- **Oficio de Comisión**: Referencia del oficio (opcional)
- **Nombramiento**: Detalles del nombramiento (opcional)
- **Asignación**: Información de asignación (opcional)
- **Observaciones**: Notas adicionales (opcional)
- **Estado**: Estado actual del acta

## 🔄 Flujo de Trabajo

1. **Creación**: Se crea el acta con información básica
2. **Edición**: Se completan los detalles y se adjuntan anexos
3. **Finalización**: Se marca como completada cuando finaliza el proceso
4. **Archivado**: El acta queda registrada en el sistema

---
*Documentación actualizada: Enero 2026*