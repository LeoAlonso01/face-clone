# 🗃️ Modelos de Base de Datos

## 📋 Tablas del Sistema

### 1. users - Usuarios del Sistema

**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L54-L70)

**Estructura**:
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    role VARCHAR DEFAULT 'USER',
    reset_token VARCHAR,
    reset_token_expiration TIMESTAMP
);
```

**Campos**:
- `id`: Identificador único (Primary Key)
- `username`: Nombre de usuario único
- `email`: Correo electrónico único
- `password`: Contraseña hasheada
- `created_at`: Timestamp de creación
- `updated_at`: Timestamp de última actualización
- `is_deleted`: Flag para soft delete
- `role`: Rol del usuario (USER, ADMIN, AUDITOR)
- `reset_token`: Token para recuperación de contraseña
- `reset_token_expiration`: Expiración del token de recuperación

### 2. unidades_responsables - Unidades Responsables

**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L74-L109)

**Estructura**:
```sql
CREATE TABLE unidades_responsables (
    id_unidad SERIAL PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    telefono VARCHAR(20),
    domicilio VARCHAR(255),
    municipio VARCHAR(100),
    localidad VARCHAR(100),
    codigo_postal VARCHAR(10),
    rfc VARCHAR(13),
    correo_electronico VARCHAR(100),
    responsable INTEGER REFERENCES users(id),
    tipo_unidad VARCHAR(50),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    fecha_cambio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unidad_padre_id INTEGER REFERENCES unidades_responsables(id_unidad)
);
```

**Campos**:
- `id_unidad`: Identificador único (Primary Key)
- `nombre`: Nombre de la unidad (requerido)
- `telefono`: Número de teléfono
- `domicilio`: Dirección física
- `municipio`: Municipio
- `localidad`: Localidad
- `codigo_postal`: Código postal
- `rfc`: RFC de la unidad
- `correo_electronico`: Correo electrónico
- `responsable`: FK a users(id) - Usuario responsable
- `tipo_unidad`: Tipo de unidad
- `fecha_creacion`: Timestamp de creación
- `fecha_cambio`: Timestamp de última modificación
- `unidad_padre_id`: FK recursiva para jerarquía

### 3. acta_entrega_recepcion - Actas de Entrega-Recepción

**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L112-L154)

**Estructura**:
```sql
CREATE TABLE acta_entrega_recepcion (
    id SERIAL PRIMARY KEY,
    unidad_responsable INTEGER NOT NULL REFERENCES unidades_responsables(id_unidad),
    folio VARCHAR,
    fecha VARCHAR,
    hora VARCHAR,
    comisionado VARCHAR,
    oficio_comision VARCHAR,
    fecha_oficio_comision VARCHAR,
    entrante VARCHAR,
    ine_entrante VARCHAR,
    fecha_inicio_labores VARCHAR,
    nombramiento VARCHAR,
    fecha_nombramiento VARCHAR,
    asignacion VARCHAR,
    asignado_por VARCHAR,
    domicilio_entrante VARCHAR,
    telefono_entrante VARCHAR,
    saliente VARCHAR,
    fecha_fin_labores VARCHAR,
    testigo_entrante VARCHAR,
    ine_testigo_entrante VARCHAR,
    testigo_saliente VARCHAR,
    ine_testigo_saliente VARCHAR,
    fecha_cierre_acta VARCHAR,
    hora_cierre_acta VARCHAR,
    observaciones TEXT,
    estado VARCHAR,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 4. anexos - Anexos Documentales

**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L155-L174)

**Estructura**:
```sql
CREATE TABLE anexos (
    id SERIAL PRIMARY KEY,
    clave VARCHAR,
    creador_id INTEGER NOT NULL REFERENCES users(id),
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    datos JSON NOT NULL,
    estado VARCHAR NOT NULL,
    unidad_responsable_id INTEGER NOT NULL REFERENCES unidades_responsables(id_unidad),
    creado_en DATE DEFAULT CURRENT_DATE,
    actualizado_en DATE DEFAULT CURRENT_DATE,
    is_deleted BOOLEAN DEFAULT FALSE,
    acta_id INTEGER REFERENCES acta_entrega_recepcion(id)
);
```

## 🔗 Relaciones entre Tablas

### Relación users ↔ unidades_responsables
```sql
-- users.responsable → unidades_responsables.id_unidad
ALTER TABLE users ADD CONSTRAINT fk_user_unidad 
    FOREIGN KEY (unidad) REFERENCES unidades_responsables(id_unidad);

-- unidades_responsables.responsable → users.id  
ALTER TABLE unidades_responsables ADD CONSTRAINT fk_unidad_responsable
    FOREIGN KEY (responsable) REFERENCES users(id);
```

### Relación unidades_responsables ↔ acta_entrega_recepcion
```sql
ALTER TABLE acta_entrega_recepcion ADD CONSTRAINT fk_acta_unidad
    FOREIGN KEY (unidad_responsable) REFERENCES unidades_responsables(id_unidad);
```

### Relación anexos ↔ múltiples tablas
```sql
-- anexos.creador_id → users.id
ALTER TABLE anexos ADD CONSTRAINT fk_anexo_creador
    FOREIGN KEY (creador_id) REFERENCES users(id);

-- anexos.unidad_responsable_id → unidades_responsables.id_unidad
ALTER TABLE anexos ADD CONSTRAINT fk_anexo_unidad
    FOREIGN KEY (unidad_responsable_id) REFERENCES unidades_responsables(id_unidad);

-- anexos.acta_id → acta_entrega_recepcion.id
ALTER TABLE anexos ADD CONSTRAINT fk_anexo_acta
    FOREIGN KEY (acta_id) REFERENCES acta_entrega_recepcion(id);
```

### Relación recursiva unidades_responsables
```sql
ALTER TABLE unidades_responsables ADD CONSTRAINT fk_unidad_padre
    FOREIGN KEY (unidad_padre_id) REFERENCES unidades_responsables(id_unidad);
```

## 🎯 Enumeraciones y Tipos

### UserRoles Enum
**Ubicación**: [models.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/models.py#L19-L22)

```python
class UserRoles(PyEnum):
    USER = "USER"
    ADMIN = "ADMIN" 
    AUDITOR = "AUDITOR"
```

## ⚙️ Configuración de Base de Datos

**Ubicación**: [database.py](file:///c:/Users/alons/OneDrive/Escritorio/SERUMICHV2BE/face-clone/backend/app/database.py)

**Configuración**:
- **Motor**: PostgreSQL con SQLAlchemy
- **Pool**: Connection pooling configurado
- **Timeout**: 30 segundos para obtener conexión
- **Recycle**: Reciclaje de conexiones cada 1 hora

**Variables de entorno**:
```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=nombre_base_datos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

## 📊 Índices y Optimización

**Índices definidos**:
- `users.username` (único)
- `users.email` (único)
- `users.id` (primary key)
- `unidades_responsables.id_unidad` (primary key)
- `unidades_responsables.nombre` (búsqueda)
- `acta_entrega_recepcion.id` (primary key)
- `anexos.id` (primary key)
- `anexos.clave` (búsqueda)
- `anexos.estado` (búsqueda)

## 🔄 Migraciones

**Ubicación**: `alembic/`

El sistema utiliza Alembic para gestionar migraciones de base de datos:

```bash
# Generar nueva migración
alembic revision --autogenerate -m "descripcion_cambios"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1
```

## 🛡️ Consideraciones de Seguridad

1. **Passwords**: Almacenadas con hash bcrypt
2. **Tokens JWT**: Firmados con clave secreta
3. **Soft Delete**: Implementado en users y anexos
4. **Validaciones**: Nivel de aplicación y base de datos
5. **Índices**: Optimizados para búsquedas frecuentes

---
*Documentación actualizada: Enero 2026*