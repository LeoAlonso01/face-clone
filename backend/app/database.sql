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


-- 1. Limpiar la tabla si es necesario (opcional)
TRUNCATE TABLE unidades_responsables RESTART IDENTITY CASCADE;

-- 2. Insertar la Rectoría (nivel raíz)
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    tipo_unidad, 
    fecha_creacion, 
    fecha_cambio
) VALUES (
    'Rectoría', 
    'Morelia', 
    'Rectoría', 
    CURRENT_TIMESTAMP, 
    CURRENT_TIMESTAMP
) RETURNING id_unidad;

-- 3. Guardamos el ID de la Rectoría para usarlo como padre
WITH rectoria AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Rectoría')

-- 4. Insertamos todas las unidades según la jerarquía del PDF
-- 4.1 Órganos directos de la Rectoría
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    tipo_unidad, 
    unidad_padre_id, 
    fecha_creacion, 
    fecha_cambio
) VALUES 
    ('Consejo de la Investigación', 'Morelia', 'Órgano de Asesoría', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad de Mediación', 'Morelia', 'Unidad', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad de Atención Integral de la Violencia de Género', 'Morelia', 'Unidad', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Coordinación General para la Igualdad de Género, Inclusión y Cultura de Paz', 'Morelia', 'Coordinación', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría Particular', 'Morelia', 'Secretaría', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría Auxiliar', 'Morelia', 'Secretaría', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Coordinación de Planeación, Infraestructura y Fortalecimiento Universitario', 'Morelia', 'Coordinación', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Tecnologías de Información y Comunicación', 'Morelia', 'Dirección', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Órgano Interno de Control', 'Morelia', 'Órgano de Control', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Tesorería', 'Morelia', 'Tesorería', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Contabilidad', 'Morelia', 'Dirección', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Fondos Extraordinarios', 'Morelia', 'Dirección', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Programación y Ejercicio del Gasto', 'Morelia', 'Dirección', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Vinculación y Servicio Social', 'Morelia', 'Dirección', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Coordinación de Proyectos Transversales y Responsabilidad Social Institucional', 'Morelia', 'Coordinación', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Transformación Digital', 'Morelia', 'Dirección', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría Administrativa', 'Morelia', 'Secretaría', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría de Difusión Cultural y Extensión Universitaria', 'Morelia', 'Secretaría', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dependencias Académicas', 'Morelia', 'Dependencia', (SELECT id_unidad FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 4.2 Unidades que dependen de otras (niveles inferiores)
-- Primero creamos CTEs para las unidades padre
WITH 
    secretaria_particular AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Secretaría Particular'),
    secretaria_auxiliar AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Secretaría Auxiliar'),
    coordinacion_planeacion AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Coordinación de Planeación, Infraestructura y Fortalecimiento Universitario'),
    direccion_tic AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Tecnologías de Información y Comunicación'),
    organo_control AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Órgano Interno de Control'),
    tesoreria AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Tesorería'),
    direccion_contabilidad AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Contabilidad'),
    direccion_fondos AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Fondos Extraordinarios'),
    direccion_programacion AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Programación y Ejercicio del Gasto'),
    direccion_vinculacion AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Vinculación y Servicio Social'),
    secretaria_administrativa AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Secretaría Administrativa'),
    secretaria_cultural AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Secretaría de Difusión Cultural y Extensión Universitaria'),
    dependencias_academicas AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dependencias Académicas')

-- Ahora insertamos las unidades dependientes
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    tipo_unidad, 
    unidad_padre_id, 
    fecha_creacion, 
    fecha_cambio
) VALUES
    -- Departamentos de Secretaría Particular
    ('Departamento de Protocolo', 'Morelia', 'Departamento', (SELECT id_unidad FROM secretaria_particular), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Auditorios, Teatros e Infraestructura Cultural', 'Morelia', 'Departamento', (SELECT id_unidad FROM secretaria_particular), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Secretaría Auxiliar
    ('Departamento de Comunicación Social', 'Morelia', 'Departamento', (SELECT id_unidad FROM secretaria_auxiliar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Comunicación Institucional', 'Morelia', 'Departamento', (SELECT id_unidad FROM secretaria_auxiliar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Subunidades de Coordinación de Planeación
    ('Departamento de Administración y Gestión', 'Morelia', 'Departamento', (SELECT id_unidad FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Planeación, Evaluación y Seguimiento', 'Morelia', 'Departamento', (SELECT id_unidad FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Información y Estadística', 'Morelia', 'Departamento', (SELECT id_unidad FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Proyectos Institucionales', 'Morelia', 'Departamento', (SELECT id_unidad FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Infraestructura Universitaria', 'Morelia', 'Subdirección', (SELECT id_unidad FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Mantenimiento y Servicios Generales Universitarios', 'Morelia', 'Subdirección', (SELECT id_unidad FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Subunidades de Dirección de TIC
    ('Subdirección de Sistemas Informáticos Académicos', 'Morelia', 'Subdirección', (SELECT id_unidad FROM direccion_tic), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Sistemas Informáticos Administrativos y Financieros', 'Morelia', 'Subdirección', (SELECT id_unidad FROM direccion_tic), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Cómputo, Software y Comunicaciones', 'Morelia', 'Subdirección', (SELECT id_unidad FROM direccion_tic), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Órgano Interno de Control
    ('Departamento de Auditoría Interna', 'Morelia', 'Departamento', (SELECT id_unidad FROM organo_control), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Investigación', 'Morelia', 'Departamento', (SELECT id_unidad FROM organo_control), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Responsabilidades Administrativas', 'Morelia', 'Departamento', (SELECT id_unidad FROM organo_control), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Tesorería
    ('Departamento de Enlace de Procesos Informáticos', 'Morelia', 'Departamento', (SELECT id_unidad FROM tesoreria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Procesos de Fiscalización y Seguimiento de Informes', 'Morelia', 'Departamento', (SELECT id_unidad FROM tesoreria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Fondos y Valores', 'Morelia', 'Departamento', (SELECT id_unidad FROM tesoreria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamento de Dirección de Contabilidad
    ('Departamento de Información Contable y Estados Financieros', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_contabilidad), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Fondos Extraordinarios
    ('Departamento de Administración de Proyectos Financiados', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_fondos), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Administración de Recursos Extraordinarios', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_fondos), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Programación
    ('Departamento de Programación y Presupuesto', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_programacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Caja Egresos', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_programacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Vinculación
    ('Departamento de Laboratorio de Conservación', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_vinculacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Servicio Social y Prácticas Profesionales', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_vinculacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Unidades de Secretaría Administrativa
    ('Dirección de Adquisiciones de Bienes y Servicios', 'Morelia', 'Dirección', (SELECT id_unidad FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Archivo', 'Morelia', 'Dirección', (SELECT id_unidad FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Control Escolar', 'Morelia', 'Dirección', (SELECT id_unidad FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Patrimonio Universitario', 'Morelia', 'Dirección', (SELECT id_unidad FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Personal', 'Morelia', 'Dirección', (SELECT id_unidad FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Unidades de Secretaría Cultural
    ('Departamento de Radio y TV Nicolaita', 'Morelia', 'Departamento', (SELECT id_unidad FROM secretaria_cultural), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Editorial y Librería Universitaria', 'Morelia', 'Departamento', (SELECT id_unidad FROM secretaria_cultural), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Deporte Universitario e Infraestructura Deportiva Universitaria', 'Morelia', 'Dirección', (SELECT id_unidad FROM secretaria_cultural), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Escuelas)
    ('Colegio Primitivo y Nacional de San Nicolás de Hidalgo', 'Morelia', 'Escuela', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Ing. Pascual Ortiz Rubio"', 'Morelia', 'Escuela', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "José María Morelos y Pavón"', 'Morelia', 'Escuela', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Isaac Arriaga"', 'Morelia', 'Escuela', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Melchor Ocampo"', 'Morelia', 'Escuela', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Gral. Lázaro Cárdenas"', 'Morelia', 'Escuela', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Lic. Eduardo Ruiz"', 'Morelia', 'Escuela', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Facultades)
    ('Facultad de Derecho y Ciencias Sociales', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Civil', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Química', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Eléctrica', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Mecánica', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería en Tecnología de la Madera', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Arquitectura', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ciencias Médicas y Biológicas "Dr. Ignacio Chávez"', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Odontología', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Químico Farmacobiología', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Enfermería', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Salud Pública y Enfermería', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Contaduría y Ciencias Administrativas', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Economía "Vasco de Quiroga"', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Medicina Veterinaria y Zootecnia', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Agrobiología "Presidente Juárez"', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ciencias Agropecuarias', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ciencias Físico Matemáticas "Mat. Luis Manuel Rivera Gutiérrez"', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Biología', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Filosofía "Dr. Samuel Ramos Magaña"', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Historia', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Psicología', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Letras', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad Popular de Bellas Artes', 'Morelia', 'Facultad', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Institutos)
    ('Instituto de Investigación en Metalurgia y Materiales', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Químico Biológicas', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Históricas', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Física y Matemáticas', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones sobre los Recursos Naturales', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Agropecuarias y Forestales', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Económicas y Empresariales', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Filosóficas "Luis Villoro Toranzo"', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones en Ciencias de la Tierra "Dr. Víctor Hugo Garduño Monroy"', 'Morelia', 'Instituto', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Unidades Profesionales)
    ('Unidad Profesional de la Ciudad de Lázaro Cárdenas', 'Lázaro Cárdenas', 'Unidad Profesional', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional de Ciudad Hidalgo', 'Ciudad Hidalgo', 'Unidad Profesional', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional del Balsas', 'Morelia', 'Unidad Profesional', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional de Uruapan', 'Uruapan', 'Unidad Profesional', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional de Zamora', 'Zamora', 'Unidad Profesional', (SELECT id_unidad FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 5. Insertar subunidades de segundo y tercer nivel (ej. departamentos dentro de direcciones)
-- Primero obtenemos IDs de las unidades padre de nivel 2
WITH 
    subdireccion_infraestructura AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Subdirección de Infraestructura Universitaria'),
    subdireccion_mantenimiento AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Subdirección de Mantenimiento y Servicios Generales Universitarios'),
    direccion_archivo AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Archivo'),
    direccion_control_escolar AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Control Escolar'),
    subdireccion_control_escolar AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Subdirección de Control Escolar'),
    subdireccion_servicios_escolares AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Subdirección de Servicios Escolares'),
    direccion_patrimonio AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Patrimonio Universitario'),
    direccion_personal AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Personal'),
    direccion_deporte AS (SELECT id_unidad FROM unidades_responsables WHERE nombre = 'Dirección de Deporte Universitario e Infraestructura Deportiva Universitaria')

-- Insertamos las unidades de tercer nivel
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    tipo_unidad, 
    unidad_padre_id, 
    fecha_creacion, 
    fecha_cambio
) VALUES
    -- Departamentos de Subdirección de Infraestructura
    ('Departamento de Proyectos y Obras', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_infraestructura), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Costos', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_infraestructura), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Archivo
    ('Departamento de Archivo Histórico', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_archivo), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Archivo de Concentración', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_archivo), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Subdirección de Control Escolar
    ('Departamento de Credenciales y Seguro Social', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Atención a Escuelas Incorporadas', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Validación y Revalidación', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Subdirección de Servicios Escolares
    ('Departamento de Posgrado', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Ingreso Escolar', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Digitalización, Informática y Estadística', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Certificados', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Permanencia Escolar', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Titulación', 'Morelia', 'Departamento', (SELECT id_unidad FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamento directo de Dirección de Control Escolar
    ('Departamento de Atención a Dependencias Descentralizadas', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Patrimonio
    ('Departamento de Control de Bienes Muebles', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_patrimonio), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Control de Bienes Inmuebles', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_patrimonio), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Control de Bienes Especializados', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_patrimonio), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Personal
    ('Departamento de Administración Laboral', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_personal), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Control y Supervisión de Personal', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_personal), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Administración de Sistemas', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_personal), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Deporte
    ('Departamento de Deporte Universitario', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_deporte), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Infraestructura Deportiva Universitaria', 'Morelia', 'Departamento', (SELECT id_unidad FROM direccion_deporte), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 6. Consulta para verificar la estructura jerárquica completa
SELECT 
    u.id_unidad,
    LPAD(' ', (LEVEL-1)*4, ' ') || u.nombre AS nombre_jerarquico,
    u.tipo_unidad,
    u.municipio,
    p.nombre AS unidad_padre
FROM 
    unidades_responsables u
LEFT JOIN 
    unidades_responsables p ON u.unidad_padre_id = p.id_unidad
START WITH 
    u.unidad_padre_id IS NULL
CONNECT BY 
    PRIOR u.id_unidad = u.unidad_padre_id
ORDER SIBLINGS BY 
    u.nombre;


WITH RECURSIVE jerarquia_completa AS (
    -- Unidades raíz (nivel superior)
    SELECT 
        id_unidad,
        nombre,
        tipo_unidad,
        unidad_padre_id,
        0 AS nivel,
        ARRAY[id_unidad] AS ruta_ids,
        nombre::TEXT AS ruta_nombres
    FROM 
        unidades_responsables
    WHERE 
        unidad_padre_id IS NULL
    
    UNION ALL
    
    -- Unidades dependientes
    SELECT 
        u.id_unidad,
        u.nombre,
        u.tipo_unidad,
        u.unidad_padre_id,
        j.nivel + 1,
        j.ruta_ids || u.id_unidad,
        j.ruta_nombres || ' > ' || u.nombre
    FROM 
        unidades_responsables u
    JOIN 
        jerarquia_completa j ON u.unidad_padre_id = j.id_unidad
)

SELECT 
    id_unidad,
    LPAD(' ', nivel*4, ' ') || nombre AS estructura_jerarquica,
    tipo_unidad,
    nivel,
    ruta_nombres AS dependencia_completa
FROM 
    jerarquia_completa
ORDER BY 
    ruta_ids;

WITH RECURSIVE jerarquia_rectoria AS (
    SELECT 
        id_unidad, nombre, tipo_unidad, unidad_padre_id, 0 AS nivel
    FROM 
        unidades_responsables 
    WHERE 
        nombre = 'Rectoría'
    
    UNION ALL
    
    SELECT 
        u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, j.nivel + 1
    FROM 
        unidades_responsables u
    JOIN 
        jerarquia_rectoria j ON u.unidad_padre_id = j.id_unidad
)

SELECT 
    LPAD(' ', nivel*4, ' ') || nombre AS estructura,
    tipo_unidad,
    nivel
FROM 
    jerarquia_rectoria
ORDER BY 
    nivel, nombre;

WITH RECURSIVE dependencias_secretaria AS (
    SELECT 
        id_unidad, nombre, tipo_unidad, unidad_padre_id, 0 AS nivel
    FROM 
        unidades_responsables 
    WHERE 
        nombre = 'Secretaría Administrativa'
    
    UNION ALL
    
    SELECT 
        u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, d.nivel + 1
    FROM 
        unidades_responsables u
    JOIN 
        dependencias_secretaria d ON u.unidad_padre_id = d.id_unidad
)

SELECT 
    LPAD(' ', nivel*4, ' ') || nombre AS estructura,
    tipo_unidad,
    nivel
FROM 
    dependencias_secretaria
ORDER BY 
    nivel, nombre;

WITH RECURSIVE dependencias_academicas AS (
    SELECT 
        id_unidad, nombre, tipo_unidad, unidad_padre_id, 0 AS nivel
    FROM 
        unidades_responsables 
    WHERE 
        nombre = 'Dependencias Académicas'
    
    UNION ALL
    
    SELECT 
        u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, d.nivel + 1
    FROM 
        unidades_responsables u
    JOIN 
        dependencias_academicas d ON u.unidad_padre_id = d.id_unidad
)

SELECT 
    LPAD(' ', nivel*4, ' ') || nombre AS estructura,
    tipo_unidad,
    nivel
FROM 
    dependencias_academicas
ORDER BY 
    nivel, nombre;

-- Cambia 'Nombre de la Unidad' por la unidad que deseas investigar
WITH RECURSIVE dependencias_unidad AS (
    SELECT 
        id_unidad, nombre, tipo_unidad, unidad_padre_id, 0 AS nivel
    FROM 
        unidades_responsables 
    WHERE 
        nombre = 'Órgano Interno de Control'  -- Cambia aquí el nombre de la unidad
    
    UNION ALL
    
    SELECT 
        u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, d.nivel + 1
    FROM 
        unidades_responsables u
    JOIN 
        dependencias_unidad d ON u.unidad_padre_id = d.id_unidad
)

SELECT 
    LPAD(' ', nivel*4, ' ') || nombre AS estructura,
    tipo_unidad,
    nivel
FROM 
    dependencias_unidad
ORDER BY 
    nivel, nombre;

WITH RECURSIVE jerarquia AS (
    SELECT 
        id_unidad, nombre, tipo_unidad, unidad_padre_id, 1 AS nivel
    FROM 
        unidades_responsables
    WHERE 
        unidad_padre_id IS NULL
    
    UNION ALL
    
    SELECT 
        u.id_unidad, u.nombre, u.tipo_unidad, u.unidad_padre_id, j.nivel + 1
    FROM 
        unidades_responsables u
    JOIN 
        jerarquia j ON u.unidad_padre_id = j.id_unidad
),

conteo_dependientes AS (
    SELECT 
        unidad_padre_id, COUNT(*) AS total_dependientes
    FROM 
        unidades_responsables
    WHERE 
        unidad_padre_id IS NOT NULL
    GROUP BY 
        unidad_padre_id
)

SELECT 
    LPAD(' ', (j.nivel-1)*4, ' ') || j.nombre AS unidad,
    j.tipo_unidad,
    j.nivel,
    COALESCE(c.total_dependientes, 0) AS dependientes_directos
FROM 
    jerarquia j
LEFT JOIN 
    conteo_dependientes c ON j.id_unidad = c.unidad_padre_id
ORDER BY 
    j.nivel, j.nombre;

-- 1. Asegurarse que la 
--tabla de usuarios existe y tiene una PK id_usuario
-- (Asumo que ya tienes una tabla users con id_usuario como PK)

-- 2. Modificar la columna responsable para que sea FK
ALTER TABLE unidades_responsables 
ALTER COLUMN responsable TYPE INTEGER USING NULL,
ALTER COLUMN responsable SET DEFAULT NULL,
ADD CONSTRAINT fk_responsable_usuario 
    FOREIGN KEY (responsable) 
    REFERENCES users(id)
    ON DELETE SET NULL;

SELECT 
    u.id_unidad,
    u.nombre AS unidad,
    u.tipo_unidad,
    us.id_usuario,
    us.nombre AS nombre_responsable,
    us.email AS email_responsable
FROM 
    unidades_responsables u
LEFT JOIN 
    users us ON u.responsable = us.id_usuario
WHERE 
    u.id_unidad = [ID_UNIDAD];

UPDATE unidades_responsables
SET responsable = [ID_USUARIO]
WHERE id_unidad = [ID_UNIDAD];