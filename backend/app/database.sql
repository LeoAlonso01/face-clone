-- Tabla que almacena los tipos de identificación de los usuarios
CREATE TABLE tipo_identificacion (
    id_tipo_ident INT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT
);

-- Tabla que almacena las unidades o departamentos dentro de la organización
CREATE TABLE unidades (
    id_unidad INT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    descripcion TEXT,
    is_deleted BOOLEAN DEFAULT FALSE -- Campo para eliminación lógica
);

-- Tabla que almacena los diferentes puestos dentro de la organización
CREATE TABLE puestos (
    id_puesto INT PRIMARY KEY,
    nombre_puesto VARCHAR(255) NOT NULL,
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha de creación del puesto
    is_deleted BOOLEAN DEFAULT FALSE, -- Campo para eliminación lógica
    nivel_jerarquico INT -- Indica la jerarquía del puesto dentro de la organización
);

-- Tabla que almacena las unidades responsables, que pueden tener una jerarquía
CREATE TABLE unidades_responsables (
    id_unidad_responsable INT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    id_padre INT REFERENCES unidades_responsables(id_unidad_responsable), -- Relación jerárquica con otra unidad responsable
    email VARCHAR(255),
    telefono VARCHAR(20),
    municipio VARCHAR(255),
    localidad VARCHAR(255),
    creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha de creación de la unidad
    id_puesto INT REFERENCES puestos(id_puesto), -- Puesto relacionado con la unidad
    departamento_id INT REFERENCES unidades(id_unidad) -- Relación con la tabla de unidades
);

-- Tabla que almacena los usuarios del sistema
CREATE TABLE usuarios (
    id_usuario INT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    username VARCHAR(255) UNIQUE NOT NULL, -- Nombre de usuario único
    password VARCHAR(255) NOT NULL, -- Contraseña del usuario (debe ser almacenada de forma segura)
    email VARCHAR(255),
    id_puesto INT REFERENCES puestos(id_puesto), -- Relación con la tabla de puestos
    rol VARCHAR(255), -- Rol del usuario dentro del sistema
    ultima_actividad TIMESTAMP, -- Última vez que el usuario realizó una acción en el sistema
    id_unidad_responsable INT REFERENCES unidades_responsables(id_unidad_responsable), -- Unidad responsable a la que pertenece
    direccion VARCHAR(255),
    telefono VARCHAR(20),
    is_deleted BOOLEAN DEFAULT FALSE -- Campo para eliminación lógica
);

-- Tabla que almacena los diferentes tipos de anexos que pueden estar vinculados a un acta
CREATE TABLE tipo_anexos (
    id_tipo_anexo INT PRIMARY KEY,
    clave_anexo VARCHAR(255) UNIQUE NOT NULL, -- Código único para identificar el tipo de anexo
    nombre VARCHAR(255),
    is_deleted BOOLEAN DEFAULT FALSE -- Campo para eliminación lógica
);

-- Tabla que almacena las actas de entrega-recepción
CREATE TABLE actas_entrega_recepcion (
    id_acta INT PRIMARY KEY,
    id_unidad_responsable INT REFERENCES unidades_responsables(id_unidad_responsable), -- Unidad responsable del acta
    fecha_acta DATE, -- Fecha de emisión del acta
    hora_acta TIME, -- Hora de emisión del acta
    termino_labores_saliente TIMESTAMP, -- Fecha y hora en que terminó el funcionario saliente
    inicio_labores_entrante TIMESTAMP, -- Fecha y hora en que inició el funcionario entrante
    fecha_conclusion_acta TIMESTAMP, -- Fecha en que se concluyó formalmente el acta
    id_usuario INT REFERENCES usuarios(id_usuario), -- Usuario que generó el acta
    id_unidad_responsable_saliente INT REFERENCES unidades_responsables(id_unidad_responsable), -- Unidad del responsable saliente
    datos_personas JSONB, -- Información de las personas involucradas en formato JSON
    observaciones TEXT, -- Observaciones del acta
    ruta_acta TEXT, -- Ruta del archivo digital del acta
    datos_firma_acta JSONB, -- Información sobre la firma del acta en formato JSON
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha de creación del acta
    fecha_edicion TIMESTAMP, -- Última fecha de edición del acta
    is_deleted BOOLEAN DEFAULT FALSE, -- Campo para eliminación lógica
    titular_entrante VARCHAR(255), -- Nombre del titular entrante
    titular_saliente VARCHAR(255), -- Nombre del titular saliente
    nombramiento TEXT -- Información sobre el nombramiento
);

-- Tabla que almacena los anexos asociados a un acta de entrega-recepción
CREATE TABLE anexos (
    id_anexo INT PRIMARY KEY,
    tipo_anexo INT REFERENCES tipo_anexos(id_tipo_anexo), -- Tipo de anexo
    creado INT REFERENCES usuarios(id_usuario), -- Usuario que creó el anexo
    contenido JSONB, -- Contenido del anexo en formato JSON
    id_acta INT REFERENCES actas_entrega_recepcion(id_acta), -- Acta a la que pertenece el anexo
    creado_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, -- Fecha de creación del anexo
    editado_at TIMESTAMP -- Última fecha de edición del anexo
);

-- Tabla que almacena reportes generados dentro del sistema
CREATE TABLE reportes (
    id_tipo_reporte INT PRIMARY KEY,
    id_anexo INT REFERENCES anexos(id_anexo), -- Relación con anexos
    nombre VARCHAR(255) NOT NULL, -- Nombre del reporte
    contenido JSONB -- Contenido del reporte en formato JSON
);

-- Tabla que almacena el historial de puestos ocupados por un usuario
CREATE TABLE historial_puestos (
    id_historial_puestos INT PRIMARY KEY,
    id_usuario INT REFERENCES usuarios(id_usuario), -- Usuario que ocupó el puesto
    id_puesto INT REFERENCES puestos(id_puesto), -- Puesto ocupado
    fecha_inicio TIMESTAMP, -- Fecha de inicio en el puesto
    fecha_fin TIMESTAMP -- Fecha de finalización en el puesto
);

