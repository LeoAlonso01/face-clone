-- Tabla roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    activo| BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Tabla permisos
CREATE TABLE permisos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Tabla intermedia roles_permisos
CREATE TABLE roles_permisos (
    rol_id INT NOT NULL,
    permiso_id INT NOT NULL,
    PRIMARY KEY (rol_id, permiso_id),
    FOREIGN KEY (rol_id) REFERENCES roles(id) ON DELETE CASCADE,
    FOREIGN KEY (permiso_id) REFERENCES permisos(id) ON DELETE CASCADE
);

-- Tabla unidades_responsables 
-- Esta tabla almacena las unidades responsables de los servidores públicos
-- incluyendo su nombre, domicilio, teléfono, municipio, correo y responsable
CREATE TABLE unidades_responsables (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    domicilio TEXT,
    telefono VARCHAR(20),
    municipio VARCHAR(50),
    correo VARCHAR(100) CHECK (correo ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    responsable INT NOT NULL  -- Este campo se usará para el usuario responsable
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    unidad_padre INT,
    nivel INT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (unidad_padre) REFERENCES unidades_responsables(id)
    FOREIGN KEY (responsable) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Tabla usuarios
CREATE TABLE usuarios (
    id SERIAL PRIMARY KEY,
    nombre_usuario VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE CHECK (email ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    contraseña VARCHAR(255) NOT NULL,
    rol_id INT NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (rol_id) REFERENCES roles(id)
);

-- Tabla claves
CREATE TABLE claves (
    id SERIAL PRIMARY KEY,
    clave VARCHAR(50) NOT NULL,
    descripcion TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Tabla anexos
CREATE TABLE anexos (
    id SERIAL PRIMARY KEY,
    clave_id INT NOT NULL,
    creador_id INT NOT NULL,
    fecha_creacion DATE NOT NULL,
    datos JSONB, -- Datos del anexo en formato JSON
    estado VARCHAR(20) NOT NULL,
    unidad_responsable_id INT NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (clave_id) REFERENCES claves(id),
    FOREIGN KEY (creador_id) REFERENCES usuarios(id),
    FOREIGN KEY (unidad_responsable_id) REFERENCES unidades_responsables(id)
);

-- Crear tipo enumerado para asignacion
CREATE TYPE tipo_asignacion AS ENUM ('Nombramiento', 'Designación', 'Jerarquia');

-- Crear tipo enumerado para asignado_por
CREATE TYPE tipo_asignado_por AS ENUM ('Rector(a)', 'H. Consejo');

-- Tabla acta_entrega_recepcion
-- Esta tabla almacena los datos de las actas de entrega-recepción
-- incluyendo los datos de los servidores públicos entrante y saliente,
CREATE TABLE acta_entrega_recepcion (
    id SERIAL PRIMARY KEY,
    folio VARCHAR(50) NOT NULL UNIQUE,
    unidad_responsable_id INT NOT NULL,
    fecha_hora TIMESTAMP WITH TIME ZONE NOT NULL,
    comisionado_id INT NOT NULL,
    oficio_comisionado VARCHAR(50),
    servidor_publico_entrante_id INT NOT NULL,
    fecha_inicio_labores DATE NOT NULL,
    telefono_entrante VARCHAR(20),
    domicilio_entrante TEXT,    
    correo_entrante VARCHAR(100) CHECK (correo_entrante ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    servidor_publico_saliente_id INT NOT NULL,
    telefono_saliente VARCHAR(20),
    domicilio_saliente TEXT,
    correo_saliente VARCHAR(100) CHECK (correo_saliente ~* '^[A-Za-z0-9._%-]+@[A-Za-z0-9.-]+[.][A-Za-z]+$'),
    fecha_termino_labores DATE NOT NULL,
    numero_nombramiento VARCHAR(50),
    fecha_nombramiento DATE,
    asignacion tipo_asignacion NOT NULL,
    asignado_por tipo_asignado_por NOT NULL,
    fecha_termino DATE,
    testigo1_tipo_id VARCHAR(20),
    testigo1_numero_id VARCHAR(20),
    testigo1_domicilio TEXT,
    testigo2_tipo_id VARCHAR(20),
    testigo2_numero_id VARCHAR(20),
    testigo2_domicilio TEXT,
    observaciones TEXT,
    normativa TEXT,
    estado VARCHAR(20) NOT NULL, -- Estado del acta
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (unidad_responsable_id) REFERENCES unidades_responsables(id),
    FOREIGN KEY (comisionado_id) REFERENCES usuarios(id),
    FOREIGN KEY (servidor_publico_entrante_id) REFERENCES usuarios(id)
    FOREIGN KEY (servidor_publico_saliente_id) REFERENCES usuarios(id)
    FOREIGN KEY (testigo1_tipo_id) REFERENCES identificacion_testigos(testigo_tipo_id),
    FOREIGN KEY (testigo2_tipo_id) REFERENCES identificacion_testigos(testigo_tipo_id),
    FOREIGN Key (estado) REFERENCES estado_acta(estado)
);

-- actas y anexos 
-- tabla intermedia para relacionar actas con anexos
CREATE TABLE actas_anexos (
    acta_id INT NOT NULL,
    anexo_id INT NOT NULL,
    PRIMARY KEY (acta_id, anexo_id),
    FOREIGN KEY (acta_id) REFERENCES acta_entrega_recepcion(id) ON DELETE CASCADE,
    FOREIGN KEY (anexo_id) REFERENCES anexos(id) ON DELETE CASCADE
);


-- Tabla estado_acta
-- Esta tabla almacena los estados posibles de un acta de entrega-recepción
CREATE TABLE estado_acta (
    id SERIAL PRIMARY KEY,
    nombre_estado VARCHAR(50) NOT NULL,
    descripcion_estado VARCHAR(100) NOT NULL,
    fecha TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Tabla identificacion_testigos
-- Esta tabla almacena los tipos de identificación de testigos
CREATE TABLE tipos_identificacion_testigos (
    testigo_tipo_id VARCHAR(20) PRIMARY KEY,
    descripcion TEXT NOT NULL,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    editado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);

-- Tabla historial_unidades
-- Esta tabla almacena el historial de cambios de unidades responsables
-- incluyendo cambios de responsable y fechas de inicio y fin
CREATE TABLE historial_unidades (
    id SERIAL PRIMARY KEY,
    unidad_id INT NOT NULL,
    responsable_id INT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    motivo_cambio TEXT,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unidad_id) REFERENCES unidades_responsables(id),
    FOREIGN KEY (responsable_id) REFERENCES usuarios(id),
    CONSTRAINT fecha_valida CHECK (fecha_fin IS NULL OR fecha_inicio <= fecha_fin)
);



-----------------------------------------------------
-- 1. Limpiar la tabla si es necesario (opcional)
TRUNCATE TABLE unidades_responsables RESTART IDENTITY CASCADE;

-- 2. Insertar la Rectoría (nivel raíz - nivel 0)
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    nivel,
    creado_en, 
    editado_en
) VALUES (
    'Rectoría', 
    'Morelia', 
    0,
    CURRENT_TIMESTAMP, 
    CURRENT_TIMESTAMP
) RETURNING id;

-- 3. Guardamos el ID de la Rectoría para usarlo como padre
WITH rectoria AS (SELECT id FROM unidades_responsables WHERE nombre = 'Rectoría')

-- 4. Insertamos todas las unidades según la jerarquía del PDF
-- 4.1 Órganos directos de la Rectoría (nivel 1)
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    nivel,
    unidad_padre, 
    creado_en, 
    editado_en
) VALUES 
    ('Consejo de la Investigación', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad de Mediación', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad de Atención Integral de la Violencia de Género', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Coordinación General para la Igualdad de Género, Inclusión y Cultura de Paz', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría Particular', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría Auxiliar', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Coordinación de Planeación, Infraestructura y Fortalecimiento Universitario', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Tecnologías de Información y Comunicación', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Órgano Interno de Control', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Tesorería', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Contabilidad', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Fondos Extraordinarios', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Programación y Ejercicio del Gasto', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Vinculación y Servicio Social', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Coordinación de Proyectos Transversales y Responsabilidad Social Institucional', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Transformación Digital', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría Administrativa', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Secretaría de Difusión Cultural y Extensión Universitaria', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dependencias Académicas', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 4.2 Unidades que dependen de otras (niveles inferiores)
-- Primero creamos CTEs para las unidades padre
WITH 
    secretaria_particular AS (SELECT id FROM unidades_responsables WHERE nombre = 'Secretaría Particular'),
    secretaria_auxiliar AS (SELECT id FROM unidades_responsables WHERE nombre = 'Secretaría Auxiliar'),
    coordinacion_planeacion AS (SELECT id FROM unidades_responsables WHERE nombre = 'Coordinación de Planeación, Infraestructura y Fortalecimiento Universitario'),
    direccion_tic AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Tecnologías de Información y Comunicación'),
    organo_control AS (SELECT id FROM unidades_responsables WHERE nombre = 'Órgano Interno de Control'),
    tesoreria AS (SELECT id FROM unidades_responsables WHERE nombre = 'Tesorería'),
    direccion_contabilidad AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Contabilidad'),
    direccion_fondos AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Fondos Extraordinarios'),
    direccion_programacion AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Programación y Ejercicio del Gasto'),
    direccion_vinculacion AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Vinculación y Servicio Social'),
    secretaria_administrativa AS (SELECT id FROM unidades_responsables WHERE nombre = 'Secretaría Administrativa'),
    secretaria_cultural AS (SELECT id FROM unidades_responsables WHERE nombre = 'Secretaría de Difusión Cultural y Extensión Universitaria'),
    dependencias_academicas AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dependencias Académicas')

-- Ahora insertamos las unidades dependientes (nivel 2)
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    nivel,
    unidad_padre, 
    creado_en, 
    editado_en
) VALUES
    -- Departamentos de Secretaría Particular
    ('Departamento de Protocolo', 'Morelia', 2, (SELECT id FROM secretaria_particular), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Auditorios, Teatros e Infraestructura Cultural', 'Morelia', 2, (SELECT id FROM secretaria_particular), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Secretaría Auxiliar
    ('Departamento de Comunicación Social', 'Morelia', 2, (SELECT id FROM secretaria_auxiliar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Comunicación Institucional', 'Morelia', 2, (SELECT id FROM secretaria_auxiliar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Subunidades de Coordinación de Planeación
    ('Departamento de Administración y Gestión', 'Morelia', 2, (SELECT id FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Planeación, Evaluación y Seguimiento', 'Morelia', 2, (SELECT id FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Información y Estadística', 'Morelia', 2, (SELECT id FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Proyectos Institucionales', 'Morelia', 2, (SELECT id FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Infraestructura Universitaria', 'Morelia', 2, (SELECT id FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Mantenimiento y Servicios Generales Universitarios', 'Morelia', 2, (SELECT id FROM coordinacion_planeacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Subunidades de Dirección de TIC
    ('Subdirección de Sistemas Informáticos Académicos', 'Morelia', 2, (SELECT id FROM direccion_tic), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Sistemas Informáticos Administrativos y Financieros', 'Morelia', 2, (SELECT id FROM direccion_tic), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Subdirección de Cómputo, Software y Comunicaciones', 'Morelia', 2, (SELECT id FROM direccion_tic), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Órgano Interno de Control
    ('Departamento de Auditoría Interna', 'Morelia', 2, (SELECT id FROM organo_control), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Investigación', 'Morelia', 2, (SELECT id FROM organo_control), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Responsabilidades Administrativas', 'Morelia', 2, (SELECT id FROM organo_control), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Tesorería
    ('Departamento de Enlace de Procesos Informáticos', 'Morelia', 2, (SELECT id FROM tesoreria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Procesos de Fiscalización y Seguimiento de Informes', 'Morelia', 2, (SELECT id FROM tesoreria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Fondos y Valores', 'Morelia', 2, (SELECT id FROM tesoreria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamento de Dirección de Contabilidad
    ('Departamento de Información Contable y Estados Financieros', 'Morelia', 2, (SELECT id FROM direccion_contabilidad), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Fondos Extraordinarios
    ('Departamento de Administración de Proyectos Financiados', 'Morelia', 2, (SELECT id FROM direccion_fondos), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Administración de Recursos Extraordinarios', 'Morelia', 2, (SELECT id FROM direccion_fondos), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Programación
    ('Departamento de Programación y Presupuesto', 'Morelia', 2, (SELECT id FROM direccion_programacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Caja Egresos', 'Morelia', 2, (SELECT id FROM direccion_programacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Vinculación
    ('Departamento de Laboratorio de Conservación', 'Morelia', 2, (SELECT id FROM direccion_vinculacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Servicio Social y Prácticas Profesionales', 'Morelia', 2, (SELECT id FROM direccion_vinculacion), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Unidades de Secretaría Administrativa
    ('Dirección de Adquisiciones de Bienes y Servicios', 'Morelia', 2, (SELECT id FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Archivo', 'Morelia', 2, (SELECT id FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Control Escolar', 'Morelia', 2, (SELECT id FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Patrimonio Universitario', 'Morelia', 2, (SELECT id FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Personal', 'Morelia', 2, (SELECT id FROM secretaria_administrativa), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Unidades de Secretaría Cultural
    ('Departamento de Radio y TV Nicolaita', 'Morelia', 2, (SELECT id FROM secretaria_cultural), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Editorial y Librería Universitaria', 'Morelia', 2, (SELECT id FROM secretaria_cultural), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Dirección de Deporte Universitario e Infraestructura Deportiva Universitaria', 'Morelia', 2, (SELECT id FROM secretaria_cultural), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Escuelas)
    ('Colegio Primitivo y Nacional de San Nicolás de Hidalgo', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Ing. Pascual Ortiz Rubio"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "José María Morelos y Pavón"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Isaac Arriaga"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Melchor Ocampo"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Gral. Lázaro Cárdenas"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Escuela Preparatoria "Lic. Eduardo Ruiz"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Facultades)
    ('Facultad de Derecho y Ciencias Sociales', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Civil', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Química', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Eléctrica', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería Mecánica', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ingeniería en Tecnología de la Madera', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Arquitectura', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ciencias Médicas y Biológicas "Dr. Ignacio Chávez"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Odontología', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Químico Farmacobiología', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Enfermería', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Salud Pública y Enfermería', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Contaduría y Ciencias Administrativas', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Economía "Vasco de Quiroga"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Medicina Veterinaria y Zootecnia', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Agrobiología "Presidente Juárez"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ciencias Agropecuarias', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Ciencias Físico Matemáticas "Mat. Luis Manuel Rivera Gutiérrez"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Biología', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Filosofía "Dr. Samuel Ramos Magaña"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Historia', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Psicología', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad de Letras', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Facultad Popular de Bellas Artes', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Institutos)
    ('Instituto de Investigación en Metalurgia y Materiales', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Químico Biológicas', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Históricas', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Física y Matemáticas', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones sobre los Recursos Naturales', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Agropecuarias y Forestales', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Económicas y Empresariales', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones Filosóficas "Luis Villoro Toranzo"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Instituto de Investigaciones en Ciencias de la Tierra "Dr. Víctor Hugo Garduño Monroy"', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Dependencias Académicas (Unidades Profesionales)
    ('Unidad Profesional de la Ciudad de Lázaro Cárdenas', 'Lázaro Cárdenas', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional de Ciudad Hidalgo', 'Ciudad Hidalgo', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional del Balsas', 'Morelia', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional de Uruapan', 'Uruapan', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Unidad Profesional de Zamora', 'Zamora', 2, (SELECT id FROM dependencias_academicas), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);

-- 5. Insertar subunidades de tercer nivel (nivel 3)
-- Primero obtenemos IDs de las unidades padre de nivel 2
WITH 
    subdireccion_infraestructura AS (SELECT id FROM unidades_responsables WHERE nombre = 'Subdirección de Infraestructura Universitaria'),
    subdireccion_mantenimiento AS (SELECT id FROM unidades_responsables WHERE nombre = 'Subdirección de Mantenimiento y Servicios Generales Universitarios'),
    direccion_archivo AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Archivo'),
    direccion_control_escolar AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Control Escolar'),
    subdireccion_control_escolar AS (SELECT id FROM unidades_responsables WHERE nombre = 'Subdirección de Control Escolar'),
    subdireccion_servicios_escolares AS (SELECT id FROM unidades_responsables WHERE nombre = 'Subdirección de Servicios Escolares'),
    direccion_patrimonio AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Patrimonio Universitario'),
    direccion_personal AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Personal'),
    direccion_deporte AS (SELECT id FROM unidades_responsables WHERE nombre = 'Dirección de Deporte Universitario e Infraestructura Deportiva Universitaria')

-- Insertamos las unidades de tercer nivel (nivel 3)
INSERT INTO unidades_responsables (
    nombre, 
    municipio, 
    nivel,
    unidad_padre, 
    creado_en, 
    editado_en
) VALUES
    -- Departamentos de Subdirección de Infraestructura
    ('Departamento de Proyectos y Obras', 'Morelia', 3, (SELECT id FROM subdireccion_infraestructura), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Costos', 'Morelia', 3, (SELECT id FROM subdireccion_infraestructura), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Archivo
    ('Departamento de Archivo Histórico', 'Morelia', 3, (SELECT id FROM direccion_archivo), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Archivo de Concentración', 'Morelia', 3, (SELECT id FROM direccion_archivo), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Subdirección de Control Escolar
    ('Departamento de Credenciales y Seguro Social', 'Morelia', 3, (SELECT id FROM subdireccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Atención a Escuelas Incorporadas', 'Morelia', 3, (SELECT id FROM subdireccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Validación y Revalidación', 'Morelia', 3, (SELECT id FROM subdireccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Subdirección de Servicios Escolares
    ('Departamento de Posgrado', 'Morelia', 3, (SELECT id FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Ingreso Escolar', 'Morelia', 3, (SELECT id FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Digitalización, Informática y Estadística', 'Morelia', 3, (SELECT id FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Certificados', 'Morelia', 3, (SELECT id FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Permanencia Escolar', 'Morelia', 3, (SELECT id FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Titulación', 'Morelia', 3, (SELECT id FROM subdireccion_servicios_escolares), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamento directo de Dirección de Control Escolar
    ('Departamento de Atención a Dependencias Descentralizadas', 'Morelia', 3, (SELECT id FROM direccion_control_escolar), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Patrimonio
    ('Departamento de Control de Bienes Muebles', 'Morelia', 3, (SELECT id FROM direccion_patrimonio), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Control de Bienes Inmuebles', 'Morelia', 3, (SELECT id FROM direccion_patrimonio), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Control de Bienes Especializados', 'Morelia', 3, (SELECT id FROM direccion_patrimonio), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Personal
    ('Departamento de Administración Laboral', 'Morelia', 3, (SELECT id FROM direccion_personal), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Control y Supervisión de Personal', 'Morelia', 3, (SELECT id FROM direccion_personal), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Administración de Sistemas', 'Morelia', 3, (SELECT id FROM direccion_personal), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    
    -- Departamentos de Dirección de Deporte
    ('Departamento de Deporte Universitario', 'Morelia', 3, (SELECT id FROM direccion_deporte), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('Departamento de Infraestructura Deportiva Universitaria', 'Morelia', 3, (SELECT id FROM direccion_deporte), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);-- 6. Consulta para verificar la estructura jerárquica completa


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