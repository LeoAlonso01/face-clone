--
-- PostgreSQL database dump
--

\restrict 4gVMnczEZa4qs1vZcgSe4XGxAEoANVouIZlFAsJVVtkDgk1DV7rFX54ybzU5XGM

-- Dumped from database version 13.22 (Debian 13.22-1.pgdg13+1)
-- Dumped by pg_dump version 13.22 (Debian 13.22-1.pgdg13+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: userroles; Type: TYPE; Schema: public; Owner: user
--

CREATE TYPE public.userroles AS ENUM (
    'USER',
    'ADMIN',
    'AUDITOR'
);


ALTER TYPE public.userroles OWNER TO "user";

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: acta_entrega_recepcion; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.acta_entrega_recepcion (
    id integer NOT NULL,
    unidad_responsable integer NOT NULL,
    folio character varying,
    fecha character varying,
    hora character varying,
    comisionado character varying,
    oficio_comision character varying,
    fecha_oficio_comision character varying,
    entrante character varying,
    ine_entrante character varying,
    fecha_inicio_labores character varying,
    nombramiento character varying,
    fecha_nombramiento character varying,
    asignacion character varying,
    asignado_por character varying,
    domicilio_entrante character varying,
    telefono_entrante character varying,
    saliente character varying,
    fecha_fin_labores character varying,
    testigo_entrante character varying,
    ine_testigo_entrante character varying,
    testigo_saliente character varying,
    ine_testigo_saliente character varying,
    fecha_cierre_acta character varying,
    hora_cierre_acta character varying,
    observaciones text,
    estado character varying,
    creado_en date,
    actualizado_en date
);


ALTER TABLE public.acta_entrega_recepcion OWNER TO "user";

--
-- Name: acta_entrega_recepcion_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.acta_entrega_recepcion_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.acta_entrega_recepcion_id_seq OWNER TO "user";

--
-- Name: acta_entrega_recepcion_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.acta_entrega_recepcion_id_seq OWNED BY public.acta_entrega_recepcion.id;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO "user";

--
-- Name: anexos; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.anexos (
    id integer NOT NULL,
    clave character varying(50),
    creador_id integer NOT NULL,
    fecha_creacion timestamp without time zone,
    datos json NOT NULL,
    estado character varying NOT NULL,
    unidad_responsable_id integer NOT NULL,
    creado_en date,
    actualizado_en date,
    is_deleted boolean,
    acta_id integer
);


ALTER TABLE public.anexos OWNER TO "user";

--
-- Name: anexos_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.anexos_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.anexos_id_seq OWNER TO "user";

--
-- Name: anexos_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.anexos_id_seq OWNED BY public.anexos.id;


--
-- Name: posts; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.posts (
    id integer NOT NULL,
    content text,
    owner_id integer,
    created_at timestamp without time zone
);


ALTER TABLE public.posts OWNER TO "user";

--
-- Name: posts_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.posts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.posts_id_seq OWNER TO "user";

--
-- Name: posts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.posts_id_seq OWNED BY public.posts.id;


--
-- Name: roles; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    nombre character varying(50) NOT NULL,
    description character varying(255),
    activo boolean,
    creado_en timestamp without time zone,
    editado_en timestamp without time zone,
    is_deleted boolean
);


ALTER TABLE public.roles OWNER TO "user";

--
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.roles_id_seq OWNER TO "user";

--
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- Name: unidades_responsables; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.unidades_responsables (
    id_unidad integer NOT NULL,
    nombre character varying(255) NOT NULL,
    telefono character varying(20),
    domicilio character varying(255),
    municipio character varying(100),
    localidad character varying(100),
    codigo_postal character varying(10),
    rfc character varying(13),
    correo_electronico character varying(100),
    responsable integer,
    tipo_unidad character varying(50),
    fecha_creacion timestamp without time zone,
    fecha_cambio timestamp without time zone,
    unidad_padre_id integer
);


ALTER TABLE public.unidades_responsables OWNER TO "user";

--
-- Name: unidades_responsables_id_unidad_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.unidades_responsables_id_unidad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.unidades_responsables_id_unidad_seq OWNER TO "user";

--
-- Name: unidades_responsables_id_unidad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.unidades_responsables_id_unidad_seq OWNED BY public.unidades_responsables.id_unidad;


--
-- Name: users; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying,
    email character varying,
    password character varying,
    created_at timestamp without time zone DEFAULT now(),
    updated_at timestamp without time zone DEFAULT now(),
    is_deleted boolean DEFAULT false,
    role public.userroles,
    reset_token text,
    reset_token_expiration timestamp without time zone
);


ALTER TABLE public.users OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.users_id_seq OWNER TO "user";

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: usuarios; Type: TABLE; Schema: public; Owner: user
--

CREATE TABLE public.usuarios (
    id integer NOT NULL,
    username character varying,
    email character varying,
    password character varying,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    is_deleted boolean,
    rol_id integer
);


ALTER TABLE public.usuarios OWNER TO "user";

--
-- Name: usuarios_id_seq; Type: SEQUENCE; Schema: public; Owner: user
--

CREATE SEQUENCE public.usuarios_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.usuarios_id_seq OWNER TO "user";

--
-- Name: usuarios_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: user
--

ALTER SEQUENCE public.usuarios_id_seq OWNED BY public.usuarios.id;


--
-- Name: acta_entrega_recepcion id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.acta_entrega_recepcion ALTER COLUMN id SET DEFAULT nextval('public.acta_entrega_recepcion_id_seq'::regclass);


--
-- Name: anexos id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.anexos ALTER COLUMN id SET DEFAULT nextval('public.anexos_id_seq'::regclass);


--
-- Name: posts id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.posts ALTER COLUMN id SET DEFAULT nextval('public.posts_id_seq'::regclass);


--
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- Name: unidades_responsables id_unidad; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.unidades_responsables ALTER COLUMN id_unidad SET DEFAULT nextval('public.unidades_responsables_id_unidad_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Name: usuarios id; Type: DEFAULT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usuarios ALTER COLUMN id SET DEFAULT nextval('public.usuarios_id_seq'::regclass);


--
-- Data for Name: acta_entrega_recepcion; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.acta_entrega_recepcion (id, unidad_responsable, folio, fecha, hora, comisionado, oficio_comision, fecha_oficio_comision, entrante, ine_entrante, fecha_inicio_labores, nombramiento, fecha_nombramiento, asignacion, asignado_por, domicilio_entrante, telefono_entrante, saliente, fecha_fin_labores, testigo_entrante, ine_testigo_entrante, testigo_saliente, ine_testigo_saliente, fecha_cierre_acta, hora_cierre_acta, observaciones, estado, creado_en, actualizado_en) FROM stdin;
5	10	FOLIO-2025-5058	2025-10-01	10:11	Leonardo Daniel Alonso Ledesma	007/2025	2025-10-01	Roberto Perez	089786	2025-10-01	Jefa de Departamento Departamento de Responsabilidades Administrativas	2025-10-01	nombramiento	rectoria	Av Madero oriente 3000	4433326811	Roberto Salinas	2025-09-30	Camila Flores	12458789	Rafael Orquin	8678678678	2025-10-01	10:12	sin observaciones 	Revisi├│n	2025-10-01	2025-10-01
6	10	FOLIO-2025-2723	2025-10-01	11:17	Maria Guadalupe Villalon Maciel	008/2025	2025-10-01	Carlos Flores	123456789	2025-09-29	Jefa del Departamento de Auditor├¡a Interna	2025-09-29	nombramiento	rectoria	Av. Cuautla #4567 Col Centro	4432449881	Roberto Salinas	2025-09-26	Camila Flores	123654789	Camilo Juarez	987654321	2025-10-03	11:19	sin observaciones 	Pendiente	2025-10-01	2025-10-01
7	212	2025-989898	2025-10-01	12:56	Maria Guadalupe Villalon Maciel	009/2025	2025-10-01	Leonardo Alonso Ledesma	089786	2025-09-29	Prueba de Desarrollo	2025-10-01	nombramiento	rectoria	Av. Cuautla #4567 Col Centro	4433326811	Roberto Salinas	2025-10-02	Camila Flores	12458789	Camilo Juarez	8678678678	2025-10-06	14:00	sin observaciones	Pendiente	2025-10-01	2025-10-01
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.alembic_version (version_num) FROM stdin;
\.


--
-- Data for Name: anexos; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.anexos (id, clave, creador_id, fecha_creacion, datos, estado, unidad_responsable_id, creado_en, actualizado_en, is_deleted, acta_id) FROM stdin;
3	RRH01	4	2025-08-23 09:15:00	[\r\n      {\r\n        "Numero de empleado": "EMP004",\r\n        "nombre": "Jorge Ram├¡rez G├│mez",\r\n        "RFC": "RAGJ870912",\r\n        "Plaza (categoria)": "Especialista",\r\n        "Tipo de encargo": "Base",\r\n        "Fecha de ingreso": "2019-11-05",\r\n        "Sueldo": "24000.00",\r\n        "Otras percepciones": "4000.00",\r\n        "Total": "28000.00",\r\n        "Unidad de Adscripcion": "Direcci├│n de Planeaci├│n",\r\n        "├ürea laboral": "An├ílisis",\r\n        "Estatus: Base, Apoyo, Comisionado": "Base"\r\n      }\r\n    ]	Completado	10	2025-08-23	2025-08-23	f	\N
2	RRH01	1	2025-08-24 10:00:00	[\r\n      {\r\n        "Numero de empleado": "EMP001",\r\n        "nombre": "Mar├¡a Garc├¡a L├│pez",\r\n        "RFC": "GALM850315",\r\n        "Plaza (categoria)": "Analista Senior",\r\n        "Tipo de encargo": "Base",\r\n        "Fecha de ingreso": "2020-03-15",\r\n        "Sueldo": "25000.00",\r\n        "Otras percepciones": "5000.00",\r\n        "Total": "30000.00",\r\n        "Unidad de Adscripcion": "Direcci├│n de Recursos Humanos",\r\n        "├ürea laboral": "Administraci├│n",\r\n        "Estatus: Base, Apoyo, Comisionado": "Base"\r\n      },\r\n      {\r\n        "Numero de empleado": "EMP002",\r\n        "nombre": "Carlos M├®ndez R├¡os",\r\n        "RFC": "MERC880722",\r\n        "Plaza (categoria)": "T├®cnico",\r\n        "Tipo de encargo": "Apoyo",\r\n        "Fecha de ingreso": "2022-01-10",\r\n        "Sueldo": "18000.00",\r\n        "Otras percepciones": "2000.00",\r\n        "Total": "20000.00",\r\n        "Unidad de Adscripcion": "Departamento de Tecnolog├¡a",\r\n        "├ürea laboral": "Soporte T├®cnico",\r\n        "Estatus: Base, Apoyo, Comisionado": "Apoyo"\r\n      },\r\n      {\r\n        "Numero de empleado": "EMP003",\r\n        "nombre": "Laura Fern├índez Torres",\r\n        "RFC": "FETL901105",\r\n        "Plaza (categoria)": "Coordinadora",\r\n        "Tipo de encargo": "Comisionado",\r\n        "Fecha de ingreso": "2023-06-01",\r\n        "Sueldo": "22000.00",\r\n        "Otras percepciones": "3000.00",\r\n        "Total": "25000.00",\r\n        "Unidad de Adscripcion": "Direcci├│n de Proyectos",\r\n        "├ürea laboral": "Gesti├│n",\r\n        "Estatus: Base, Apoyo, Comisionado": "Comisionado"\r\n      }\r\n    ]	Completado	212	2025-08-24	2025-08-24	f	7
1	MJ01	1	2025-08-24 00:00:00	[{"ordenamiento": "1", "Titulo": "Ley de Transparencia", "Fecha de emision": "2025-01-01"}, {"ORDENAMIENTO": "Ley", "TITULO": "Ley Organica de la Universidad Michoacana de San Nicolas de Hidalgo", "FECHA DE EMISION": "2025-10-03"}]	Revisi├│n	212	2025-08-24	2025-10-30	f	7
12	PP01	1	2025-09-09 00:00:00	[{"url": [{"url": "http://localhost:8000/static/pdfs/20250917_205221_reporte-semanal-Leonardo-Daniel-Alonso-2025-08-22.pdf"}]}]	Borrador	212	2025-09-17	2025-09-17	f	7
14	RF06	1	2025-11-03 00:00:00	[{"OFICIO DE AUTORIZACION NUM.": "of-008", "DE FECHA": "12-12-2020", "NOMBRE DEL RESPONSABLE": "Leonardo Daniel Alonso", "CARGO DEL RESPONSABLE": "PSP", "IMPORTE AL VERIFICAR": "1000", "DESTINO DEL FONDO ASIGNADO": "Compras", "RESULTADO DEL ULTIMO ARQUEO PRACTICADO": "100", "SALDO EN CUENTA DE CHEQUES": "0", "NO. DE CUENTA": "0098987789", "BANCO": "Azteca", "FECHA": "12-02-2021", "SALDO": "700", "MONTO DISPONIBLE EN EFECTIVO": "0", "COMPROBANTES": "n/A", "ACREEDORES DIVERSOS": "S/A", "DEUDORES DIVERSOS": "N/A", "DOCUMENTOS POR RECUPERAR": "N/A"}, {"OFICIO DE AUTORIZACION NUM.": "of.9099", "DE FECHA": "12-3-2021", "NOMBRE DEL RESPONSABLE": "Juan Perez", "CARGO DEL RESPONSABLE": "Auxiliar", "IMPORTE AL VERIFICAR": "100", "DESTINO DEL FONDO ASIGNADO": "Compras", "RESULTADO DEL ULTIMO ARQUEO PRACTICADO": "20", "SALDO EN CUENTA DE CHEQUES": "45", "NO. DE CUENTA": "61785285887168", "BANCO": "BBVA", "FECHA": "12-04-2022", "SALDO": "0", "MONTO DISPONIBLE EN EFECTIVO": "0", "COMPROBANTES": "N/A", "ACREEDORES DIVERSOS": "N/A", "DEUDORES DIVERSOS": "N/A", "DOCUMENTOS POR RECUPERAR": "N/A"}]	Borrador	212	2025-11-03	2025-11-03	f	7
13	RF04	1	2025-10-01 00:00:00	[{"NOMBRE DEL PROGRAMA": "Programa Piloto", "NUMERO DEL CAPITULO": "0082", "NOMBRE DEL CAPITULO": "Sin nombre", "PRESUPUESTO": "10000", "AUTORIZADO": "12000", "AMPLIACIONES Y/O REDUCCIONES": "sin ampliaciones", "MODIFICADO": "sin modificaciones", "EJERCIDO": "8000", "POR EJERCER": "4000"}]	Borrador	212	2025-10-30	2025-10-30	f	7
8	AR01	1	2025-08-27 00:00:00	[{"S\\u00edntesis del Asunto": "SEGUIMIENTO AL PROGRAMA PARA EL DESARROLLO PROFESIONAL DOCENTE (PRODEP) 2024", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SOLICITAR AL SECRETARIO ACADEMICO EL CONVENIO QUE LA UNIVERSIDAD MICHOACANA DE SAN NICOLAS DE HIDALGO, HAYA FIRMADO CON  LA SEP Y EL SECRETARIO DE FINANZAS Y ADMINISTRACION DEL ESTADO DE MICHOACAN, ASI COMO LA DEMAS DOCUMENTACION REFERENTE A DICHO PROGRAMA PRESUPUESTARIO S247 PARA EL DESAARROLLO PROFESIONAL DOCENTE  DEL EJERCICIO FISCAL 2024"}, {"S\\u00edntesis del Asunto": "AUDITORIA A LA URE: 307 INSTITUTO DE INVESTICACIONES ECONOMICAS Y EMPRESARIALES, DAI/001/2024", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SE INICIO EL DIA 22 DE ENERO DEL 2024, CON LA ORDEN NUMERO DAI/001/2024 Y CON EL OFICIO 015/2024/DAI, EN LA CUAL SE ENCUENTRA EN ANALISIS LA INFORMACION PROPORCIONADA."}, {"S\\u00edntesis del Asunto": "FALTA CERRAR 11 NUMERO DE ACTAS DE ENTREGA - RECEPCION CORRESPONDIENTES AL EJERCICIO FISCAL 2024", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "COORDINARSE CON LAS COMPA\\u00d1ERAS DE ENTREGA-RECEPCION PARA LLEVAR A CABO LOS PROCESOS."}, {"S\\u00edntesis del Asunto": "REVISAR CON LA CONTADORA NIDIA, CUAL FUE EL RESULTADO DEL CONTEO DE LA DIGITALIZACION DE LAS NOMINAS DEL 2023, PARA LAS QUE FALTEN NOS DIGITALIZEN 2024.", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SE COTIZO EL SERVICIO DE DIGITALIZACION POR LA CANTIDAD DE XXX NUMERO DE HOJAS, SIN EMBARGO SE ESTA EN REVISION, TODA VEZ QUE EL NUMERO FUE MENOR, POR LO QUE HABRA QUE COTEJAR EL IMPORTE CON EL ING. SOSTENES, PARA QUE LAS HOJAS FALTANTES POR DIGITALIZAR, SEAN DEL EJERCICIO FISCAL 2024 DE LAS NOMINAS."}, {"S\\u00edntesis del Asunto": "ACTIVIDADES POLITICO EMPRESARIALES SECCION , FACULTAD DE DERECHO, URUAPAN MICHOACAN", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SE EMITIO ACUERDO DE CONCLUSION Y ARCHIVO"}, {"S\\u00edntesis del Asunto": "INDEBIDO PROCESO DE ASIGNACION PARA PAGO DE FACTURA  UMSNH", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SE DICTO ACUERDO DE CONCLUSION Y ARCHIVO"}, {"S\\u00edntesis del Asunto": "OBSERVACIONES DE AUDITORIA UMSNH", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SE ACUMULA AL 02/2024 POR TRATARSE DEL MISMO ASUNTO"}, {"S\\u00edntesis del Asunto": "AUDITORIA FACULTAD DE ECONOMIA", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SEGUIMIENTO"}, {"S\\u00edntesis del Asunto": "AUDITORIA UNIDAD PROFESIONAL DE LA CIUDAD DE LAZARO CARDENAS", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "SEGUIMIENTO"}, {"S\\u00edntesis del Asunto": "AUDITORIA COORDINACION DE INVESTIGACION CIENTIFICA", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "EN PLAZO DE 30 DIAS PARA ATENDER PRELIMINARES "}, {"S\\u00edntesis del Asunto": "AUDITORIA FACULTAD DE PSICOLOGIA", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "AUDITORIA COLEGIO PRIMITIVO Y NACIONAL DE SAN NICOLAS DE HIDALGO", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "EN PLAZO DE 30 DIAS PARA ATENDER PRELIMINARES "}, {"S\\u00edntesis del Asunto": "AUDITORIA ESCUELA PREPARATORIA JOSE MA MORELOS Y PAVON ", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "EN PLAZO DE 30 DIAS PARA ATENDER PRELIMINARES "}, {"S\\u00edntesis del Asunto": "AUDITORIA PROGRAMA DE SERVICIO SOCIAL", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "AUDITORIA DIRECCION DE PATRIMONIO", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "AUDITORIA FACULTAD DE ODONTOLOGIA ", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "AUDITORIA FACULTAD DE ECONOMIA ", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "AUDITORIA DEPARTAMENTO DEL DEPORTE ", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "AUDITORIA FACULTAD DE MEDICINA Y CIENCIAS BIOLOGICAS \\"DR. IGNACIO CHAVEZ\\" ", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "AUDITORIA DEPARTAMENTO EDITORIAL Y LIBRER\\u00cdA UNIVERSITARIA ", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITOR\\u00cdA INTERNA ", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CURSO"}, {"S\\u00edntesis del Asunto": "EXPEDIENTE JDAI/EI/018/2023 DEPOSITOS INDEBIDOS FACULTAD POPULAR DE BELLAS ARTES ", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITORIA INTERNA", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "CONCLUIDO"}, {"S\\u00edntesis del Asunto": "EXPEDIENTE EI/42/2024 DENUNCIANTE DR. RAUL CARRERA CASTILLO, ABOGADO GENERAL DE LA UMSNH", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITORIA INTERNA", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "PARA CIERRE DE INVESTIGACION"}, {"S\\u00edntesis del Asunto": "EXPEDIENTE EI/43/2024 DENUNCIANTE DRA. LAURA LETICIA PADILLA GIL", "\\u00c1rea Responsable": "DEPARTAMENTO DE AUDITORIA INTERNA", "Fecha de Atenci\\u00f3n": "Otro", "Observaciones": "EN INICIO DE INVESTIGACION"}]	Revisi├│n	212	2025-08-27	2025-10-30	f	7
\.


--
-- Data for Name: posts; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.posts (id, content, owner_id, created_at) FROM stdin;
\.


--
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.roles (id, nombre, description, activo, creado_en, editado_en, is_deleted) FROM stdin;
\.


--
-- Data for Name: unidades_responsables; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.unidades_responsables (id_unidad, nombre, telefono, domicilio, municipio, localidad, codigo_postal, rfc, correo_electronico, responsable, tipo_unidad, fecha_creacion, fecha_cambio, unidad_padre_id) FROM stdin;
1	Rector├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Rector├¡a	2025-06-09 20:50:56.058313	2025-06-09 20:50:56.058313	\N
2	Consejo de la Investigaci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	├ôrgano de Asesor├¡a	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
3	Unidad de Mediaci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Unidad	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
4	Unidad de Atenci├│n Integral de la Violencia de G├®nero	\N	\N	Morelia	\N	\N	\N	\N	\N	Unidad	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
5	Coordinaci├│n General para la Igualdad de G├®nero, Inclusi├│n y Cultura de Paz	\N	\N	Morelia	\N	\N	\N	\N	\N	Coordinaci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
6	Secretar├¡a Particular	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
7	Secretar├¡a Auxiliar	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
8	Coordinaci├│n de Planeaci├│n, Infraestructura y Fortalecimiento Universitario	\N	\N	Morelia	\N	\N	\N	\N	\N	Coordinaci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
9	Direcci├│n de Tecnolog├¡as de Informaci├│n y Comunicaci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
10	├ôrgano Interno de Control	\N	\N	Morelia	\N	\N	\N	\N	\N	├ôrgano de Control	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
11	Tesorer├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Tesorer├¡a	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
12	Direcci├│n de Contabilidad	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
13	Direcci├│n de Fondos Extraordinarios	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
14	Direcci├│n de Programaci├│n y Ejercicio del Gasto	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
15	Direcci├│n de Vinculaci├│n y Servicio Social	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
16	Coordinaci├│n de Proyectos Transversales y Responsabilidad Social Institucional	\N	\N	Morelia	\N	\N	\N	\N	\N	Coordinaci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
17	Direcci├│n de Transformaci├│n Digital	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
18	Secretar├¡a Administrativa	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
19	Secretar├¡a de Difusi├│n Cultural y Extensi├│n Universitaria	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
20	Dependencias Acad├®micas	\N	\N	Morelia	\N	\N	\N	\N	\N	Dependencia	2025-06-09 20:50:56.093184	2025-06-09 20:50:56.093184	1
21	Departamento de Protocolo	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	6
22	Departamento de Auditorios, Teatros e Infraestructura Cultural	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	6
23	Departamento de Comunicaci├│n Social	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	7
24	Departamento de Comunicaci├│n Institucional	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	7
25	Departamento de Administraci├│n y Gesti├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	8
26	Departamento de Planeaci├│n, Evaluaci├│n y Seguimiento	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	8
27	Departamento de Informaci├│n y Estad├¡stica	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	8
28	Departamento de Proyectos Institucionales	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	8
29	Subdirecci├│n de Infraestructura Universitaria	\N	\N	Morelia	\N	\N	\N	\N	\N	Subdirecci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	8
30	Subdirecci├│n de Mantenimiento y Servicios Generales Universitarios	\N	\N	Morelia	\N	\N	\N	\N	\N	Subdirecci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	8
31	Subdirecci├│n de Sistemas Inform├íticos Acad├®micos	\N	\N	Morelia	\N	\N	\N	\N	\N	Subdirecci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	9
32	Subdirecci├│n de Sistemas Inform├íticos Administrativos y Financieros	\N	\N	Morelia	\N	\N	\N	\N	\N	Subdirecci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	9
33	Subdirecci├│n de C├│mputo, Software y Comunicaciones	\N	\N	Morelia	\N	\N	\N	\N	\N	Subdirecci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	9
34	Departamento de Auditor├¡a Interna	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	10
35	Departamento de Investigaci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	10
36	Departamento de Responsabilidades Administrativas	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	10
37	Departamento de Enlace de Procesos Inform├íticos	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	11
38	Departamento de Procesos de Fiscalizaci├│n y Seguimiento de Informes	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	11
39	Departamento de Fondos y Valores	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	11
40	Departamento de Informaci├│n Contable y Estados Financieros	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	12
41	Departamento de Administraci├│n de Proyectos Financiados	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	13
42	Departamento de Administraci├│n de Recursos Extraordinarios	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	13
43	Departamento de Programaci├│n y Presupuesto	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	14
44	Departamento de Caja Egresos	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	14
45	Departamento de Laboratorio de Conservaci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	15
46	Departamento de Servicio Social y Pr├ícticas Profesionales	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	15
47	Direcci├│n de Adquisiciones de Bienes y Servicios	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	18
48	Direcci├│n de Archivo	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	18
49	Direcci├│n de Control Escolar	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	18
50	Direcci├│n de Patrimonio Universitario	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	18
51	Direcci├│n de Personal	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	18
52	Departamento de Radio y TV Nicolaita	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	19
53	Departamento de Editorial y Librer├¡a Universitaria	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	19
54	Direcci├│n de Deporte Universitario e Infraestructura Deportiva Universitaria	\N	\N	Morelia	\N	\N	\N	\N	\N	Direcci├│n	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	19
55	Colegio Primitivo y Nacional de San Nicol├ís de Hidalgo	\N	\N	Morelia	\N	\N	\N	\N	\N	Escuela	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
56	Escuela Preparatoria "Ing. Pascual Ortiz Rubio"	\N	\N	Morelia	\N	\N	\N	\N	\N	Escuela	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
57	Escuela Preparatoria "Jos├® Mar├¡a Morelos y Pav├│n"	\N	\N	Morelia	\N	\N	\N	\N	\N	Escuela	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
58	Escuela Preparatoria "Isaac Arriaga"	\N	\N	Morelia	\N	\N	\N	\N	\N	Escuela	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
59	Escuela Preparatoria "Melchor Ocampo"	\N	\N	Morelia	\N	\N	\N	\N	\N	Escuela	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
60	Escuela Preparatoria "Gral. L├ízaro C├írdenas"	\N	\N	Morelia	\N	\N	\N	\N	\N	Escuela	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
61	Escuela Preparatoria "Lic. Eduardo Ruiz"	\N	\N	Morelia	\N	\N	\N	\N	\N	Escuela	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
62	Facultad de Derecho y Ciencias Sociales	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
63	Facultad de Ingenier├¡a Civil	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
64	Facultad de Ingenier├¡a Qu├¡mica	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
65	Facultad de Ingenier├¡a El├®ctrica	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
66	Facultad de Ingenier├¡a Mec├ínica	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
67	Facultad de Ingenier├¡a en Tecnolog├¡a de la Madera	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
68	Facultad de Arquitectura	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
69	Facultad de Ciencias M├®dicas y Biol├│gicas "Dr. Ignacio Ch├ívez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
70	Facultad de Odontolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
71	Facultad de Qu├¡mico Farmacobiolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
72	Facultad de Enfermer├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
73	Facultad de Salud P├║blica y Enfermer├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
74	Facultad de Contadur├¡a y Ciencias Administrativas	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
75	Facultad de Econom├¡a "Vasco de Quiroga"	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
76	Facultad de Medicina Veterinaria y Zootecnia	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
77	Facultad de Agrobiolog├¡a "Presidente Ju├írez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
78	Facultad de Ciencias Agropecuarias	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
79	Facultad de Ciencias F├¡sico Matem├íticas "Mat. Luis Manuel Rivera Guti├®rrez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
80	Facultad de Biolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
81	Facultad de Filosof├¡a "Dr. Samuel Ramos Maga├▒a"	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
82	Facultad de Historia	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
83	Facultad de Psicolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
84	Facultad de Letras	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
85	Facultad Popular de Bellas Artes	\N	\N	Morelia	\N	\N	\N	\N	\N	Facultad	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
86	Instituto de Investigaci├│n en Metalurgia y Materiales	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
87	Instituto de Investigaciones Qu├¡mico Biol├│gicas	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
88	Instituto de Investigaciones Hist├│ricas	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
89	Instituto de F├¡sica y Matem├íticas	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
90	Instituto de Investigaciones sobre los Recursos Naturales	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
91	Instituto de Investigaciones Agropecuarias y Forestales	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
92	Instituto de Investigaciones Econ├│micas y Empresariales	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
93	Instituto de Investigaciones Filos├│ficas "Luis Villoro Toranzo"	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
94	Instituto de Investigaciones en Ciencias de la Tierra "Dr. V├¡ctor Hugo Gardu├▒o Monroy"	\N	\N	Morelia	\N	\N	\N	\N	\N	Instituto	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
95	Unidad Profesional de la Ciudad de L├ízaro C├írdenas	\N	\N	L├ízaro C├írdenas	\N	\N	\N	\N	\N	Unidad Profesional	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
96	Unidad Profesional de Ciudad Hidalgo	\N	\N	Ciudad Hidalgo	\N	\N	\N	\N	\N	Unidad Profesional	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
97	Unidad Profesional del Balsas	\N	\N	Morelia	\N	\N	\N	\N	\N	Unidad Profesional	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
98	Unidad Profesional de Uruapan	\N	\N	Uruapan	\N	\N	\N	\N	\N	Unidad Profesional	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
99	Unidad Profesional de Zamora	\N	\N	Zamora	\N	\N	\N	\N	\N	Unidad Profesional	2025-06-09 20:50:56.177116	2025-06-09 20:50:56.177116	20
100	Departamento de Proyectos y Obras	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	29
101	Departamento de Costos	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	29
113	Departamento de Atenci├│n a Dependencias Descentralizadas	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
114	Departamento de Control de Bienes Muebles	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	50
115	Departamento de Control de Bienes Inmuebles	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	50
116	Departamento de Control de Bienes Especializados	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	50
117	Departamento de Administraci├│n Laboral	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	51
118	Departamento de Control y Supervisi├│n de Personal	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	51
119	Departamento de Administraci├│n de Sistemas	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	51
120	Departamento de Deporte Universitario	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	54
121	Departamento de Infraestructura Deportiva Universitaria	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	54
104	Departamento de Credenciales y Seguro Social	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
105	Departamento de Atenci├│n a Escuelas Incorporadas	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
103	Departamento de Archivo de Concentraci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	48
102	Departamento de Archivo Hist├│rico	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	48
106	Departamento de Validaci├│n y Revalidaci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
107	Departamento de Posgrado	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
108	Departamento de Ingreso Escolar	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
109	Departamento de Digitalizaci├│n, Inform├ítica y Estad├¡stica	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
110	Departamento de Certificados	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
111	Departamento de Permanencia Escolar	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
112	Departamento de Titulaci├│n	\N	\N	Morelia	\N	\N	\N	\N	\N	Departamento	2025-06-09 20:50:56.238546	2025-06-09 20:50:56.238546	49
122	Secretar├¡a Acad├®mica de Colegio Primitivo y Nacional de San Nicol├ís de Hidalgo	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	55
123	Secretar├¡a Administrativa de Colegio Primitivo y Nacional de San Nicol├ís de Hidalgo	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	55
124	Secretar├¡a Acad├®mica de Escuela Preparatoria "Ing. Pascual Ortiz Rubio"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	56
125	Secretar├¡a Administrativa de Escuela Preparatoria "Ing. Pascual Ortiz Rubio"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	56
126	Secretar├¡a Acad├®mica de Escuela Preparatoria "Jos├® Mar├¡a Morelos y Pav├│n"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	57
127	Secretar├¡a Administrativa de Escuela Preparatoria "Jos├® Mar├¡a Morelos y Pav├│n"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	57
128	Secretar├¡a Acad├®mica de Escuela Preparatoria "Isaac Arriaga"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	58
129	Secretar├¡a Administrativa de Escuela Preparatoria "Isaac Arriaga"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	58
130	Secretar├¡a Acad├®mica de Escuela Preparatoria "Melchor Ocampo"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	59
131	Secretar├¡a Administrativa de Escuela Preparatoria "Melchor Ocampo"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	59
132	Secretar├¡a Acad├®mica de Escuela Preparatoria "Gral. L├ízaro C├írdenas"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	60
133	Secretar├¡a Administrativa de Escuela Preparatoria "Gral. L├ízaro C├írdenas"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	60
134	Secretar├¡a Acad├®mica de Escuela Preparatoria "Lic. Eduardo Ruiz"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	61
135	Secretar├¡a Administrativa de Escuela Preparatoria "Lic. Eduardo Ruiz"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	61
136	Secretar├¡a Acad├®mica de Facultad de Derecho y Ciencias Sociales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	62
137	Secretar├¡a Administrativa de Facultad de Derecho y Ciencias Sociales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	62
138	Secretar├¡a Acad├®mica de Facultad de Ingenier├¡a Civil	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	63
139	Secretar├¡a Administrativa de Facultad de Ingenier├¡a Civil	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	63
140	Secretar├¡a Acad├®mica de Facultad de Ingenier├¡a Qu├¡mica	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	64
141	Secretar├¡a Administrativa de Facultad de Ingenier├¡a Qu├¡mica	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	64
142	Secretar├¡a Acad├®mica de Facultad de Ingenier├¡a El├®ctrica	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	65
143	Secretar├¡a Administrativa de Facultad de Ingenier├¡a El├®ctrica	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	65
144	Secretar├¡a Acad├®mica de Facultad de Ingenier├¡a Mec├ínica	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	66
145	Secretar├¡a Administrativa de Facultad de Ingenier├¡a Mec├ínica	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	66
146	Secretar├¡a Acad├®mica de Facultad de Ingenier├¡a en Tecnolog├¡a de la Madera	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	67
147	Secretar├¡a Administrativa de Facultad de Ingenier├¡a en Tecnolog├¡a de la Madera	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	67
148	Secretar├¡a Acad├®mica de Facultad de Arquitectura	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	68
149	Secretar├¡a Administrativa de Facultad de Arquitectura	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	68
150	Secretar├¡a Acad├®mica de Facultad de Ciencias M├®dicas y Biol├│gicas "Dr. Ignacio Ch├ívez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	69
151	Secretar├¡a Administrativa de Facultad de Ciencias M├®dicas y Biol├│gicas "Dr. Ignacio Ch├ívez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	69
152	Secretar├¡a Acad├®mica de Facultad de Odontolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	70
153	Secretar├¡a Administrativa de Facultad de Odontolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	70
154	Secretar├¡a Acad├®mica de Facultad de Qu├¡mico Farmacobiolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	71
155	Secretar├¡a Administrativa de Facultad de Qu├¡mico Farmacobiolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	71
156	Secretar├¡a Acad├®mica de Facultad de Enfermer├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	72
157	Secretar├¡a Administrativa de Facultad de Enfermer├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	72
158	Secretar├¡a Acad├®mica de Facultad de Salud P├║blica y Enfermer├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	73
159	Secretar├¡a Administrativa de Facultad de Salud P├║blica y Enfermer├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	73
160	Secretar├¡a Acad├®mica de Facultad de Contadur├¡a y Ciencias Administrativas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	74
161	Secretar├¡a Administrativa de Facultad de Contadur├¡a y Ciencias Administrativas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	74
162	Secretar├¡a Acad├®mica de Facultad de Econom├¡a "Vasco de Quiroga"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	75
163	Secretar├¡a Administrativa de Facultad de Econom├¡a "Vasco de Quiroga"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	75
164	Secretar├¡a Acad├®mica de Facultad de Medicina Veterinaria y Zootecnia	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	76
165	Secretar├¡a Administrativa de Facultad de Medicina Veterinaria y Zootecnia	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	76
166	Secretar├¡a Acad├®mica de Facultad de Agrobiolog├¡a "Presidente Ju├írez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	77
167	Secretar├¡a Administrativa de Facultad de Agrobiolog├¡a "Presidente Ju├írez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	77
168	Secretar├¡a Acad├®mica de Facultad de Ciencias Agropecuarias	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	78
169	Secretar├¡a Administrativa de Facultad de Ciencias Agropecuarias	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	78
170	Secretar├¡a Acad├®mica de Facultad de Ciencias F├¡sico Matem├íticas "Mat. Luis Manuel Rivera Guti├®rrez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	79
171	Secretar├¡a Administrativa de Facultad de Ciencias F├¡sico Matem├íticas "Mat. Luis Manuel Rivera Guti├®rrez"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	79
172	Secretar├¡a Acad├®mica de Facultad de Biolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	80
173	Secretar├¡a Administrativa de Facultad de Biolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	80
174	Secretar├¡a Acad├®mica de Facultad de Filosof├¡a "Dr. Samuel Ramos Maga├▒a"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	81
175	Secretar├¡a Administrativa de Facultad de Filosof├¡a "Dr. Samuel Ramos Maga├▒a"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	81
176	Secretar├¡a Acad├®mica de Facultad de Historia	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	82
177	Secretar├¡a Administrativa de Facultad de Historia	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	82
178	Secretar├¡a Acad├®mica de Facultad de Psicolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	83
179	Secretar├¡a Administrativa de Facultad de Psicolog├¡a	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	83
180	Secretar├¡a Acad├®mica de Facultad de Letras	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	84
181	Secretar├¡a Administrativa de Facultad de Letras	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	84
182	Secretar├¡a Acad├®mica de Facultad Popular de Bellas Artes	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	85
183	Secretar├¡a Administrativa de Facultad Popular de Bellas Artes	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	85
184	Secretar├¡a Acad├®mica de Instituto de Investigaci├│n en Metalurgia y Materiales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	86
185	Secretar├¡a Administrativa de Instituto de Investigaci├│n en Metalurgia y Materiales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	86
186	Secretar├¡a Acad├®mica de Instituto de Investigaciones Qu├¡mico Biol├│gicas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	87
187	Secretar├¡a Administrativa de Instituto de Investigaciones Qu├¡mico Biol├│gicas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	87
188	Secretar├¡a Acad├®mica de Instituto de Investigaciones Hist├│ricas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	88
189	Secretar├¡a Administrativa de Instituto de Investigaciones Hist├│ricas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	88
190	Secretar├¡a Acad├®mica de Instituto de F├¡sica y Matem├íticas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	89
191	Secretar├¡a Administrativa de Instituto de F├¡sica y Matem├íticas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	89
192	Secretar├¡a Acad├®mica de Instituto de Investigaciones sobre los Recursos Naturales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	90
193	Secretar├¡a Administrativa de Instituto de Investigaciones sobre los Recursos Naturales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	90
194	Secretar├¡a Acad├®mica de Instituto de Investigaciones Agropecuarias y Forestales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	91
195	Secretar├¡a Administrativa de Instituto de Investigaciones Agropecuarias y Forestales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	91
196	Secretar├¡a Acad├®mica de Instituto de Investigaciones Econ├│micas y Empresariales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	92
197	Secretar├¡a Administrativa de Instituto de Investigaciones Econ├│micas y Empresariales	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	92
198	Secretar├¡a Acad├®mica de Instituto de Investigaciones Filos├│ficas "Luis Villoro Toranzo"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	93
199	Secretar├¡a Administrativa de Instituto de Investigaciones Filos├│ficas "Luis Villoro Toranzo"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	93
200	Secretar├¡a Acad├®mica de Instituto de Investigaciones en Ciencias de la Tierra "Dr. V├¡ctor Hugo Gardu├▒o Monroy"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	94
201	Secretar├¡a Administrativa de Instituto de Investigaciones en Ciencias de la Tierra "Dr. V├¡ctor Hugo Gardu├▒o Monroy"	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	94
202	Secretar├¡a Acad├®mica de Unidad Profesional de la Ciudad de L├ízaro C├írdenas	\N	\N	L├ízaro C├írdenas	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	95
203	Secretar├¡a Administrativa de Unidad Profesional de la Ciudad de L├ízaro C├írdenas	\N	\N	L├ízaro C├írdenas	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	95
204	Secretar├¡a Acad├®mica de Unidad Profesional de Ciudad Hidalgo	\N	\N	Ciudad Hidalgo	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	96
205	Secretar├¡a Administrativa de Unidad Profesional de Ciudad Hidalgo	\N	\N	Ciudad Hidalgo	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	96
206	Secretar├¡a Acad├®mica de Unidad Profesional del Balsas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	97
207	Secretar├¡a Administrativa de Unidad Profesional del Balsas	\N	\N	Morelia	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	97
208	Secretar├¡a Acad├®mica de Unidad Profesional de Uruapan	\N	\N	Uruapan	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	98
209	Secretar├¡a Administrativa de Unidad Profesional de Uruapan	\N	\N	Uruapan	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	98
210	Secretar├¡a Acad├®mica de Unidad Profesional de Zamora	\N	\N	Zamora	\N	\N	\N	\N	\N	Secretar├¡a Acad├®mica	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	99
211	Secretar├¡a Administrativa de Unidad Profesional de Zamora	\N	\N	Zamora	\N	\N	\N	\N	\N	Secretar├¡a Administrativa	2025-08-05 18:52:43.929039	2025-08-05 18:52:43.929039	99
212	Unidad de Prueba Desarrollo	5551234567	Calle Falsa 123	Ciudad de M├®xico	Centro	06000	XAXX010101000	prueba@dev.com	1	Departamento	\N	\N	\N
300	Departamento de Acreditaci├│n y Evaluaci├│n	3115550101	Edificio Administrativo, Piso 3	Morelia	Ciudad Universitaria	58000	DAE999999XX1	acreditacion@prueba.edu.mx	\N	ADMINISTRATIVA	2025-10-07 20:13:26.792415	2025-10-07 20:13:26.792415	212
302	Direcci├│n de Finanzas	3115550103	Edificio Administrativo, Piso 4	Morelia	Ciudad Universitaria	58000	DFI999999XX3	finanzas@prueba.edu.mx	\N	ADMINISTRATIVA	2025-10-07 20:13:26.792415	2025-10-07 20:13:26.792415	212
303	Departamento de Auditor├¡a Interna	3115550104	Edificio Administrativo, Subdirecci├│n de Control	Morelia	Ciudad Universitaria	58000	DAI999999XX4	auditoria@prueba.edu.mx	\N	ADMINISTRATIVA	2025-10-07 20:13:26.792415	2025-10-07 20:13:26.792415	212
304	Facultad de Ciencias de la Educaci├│n	3115550201	Boulevard Madero Poniente 1234	Morelia	Zona Centro	58000	FCE999999XX5	educacion@prueba.edu.mx	\N	ACADEMICA	2025-10-07 20:13:26.792415	2025-10-07 20:13:26.792415	212
305	Escuela de Posgrado	3115550202	Avenida Ju├írez 567	Morelia	Centro Hist├│rico	58000	EPG999999XX6	posgrado@prueba.edu.mx	\N	ACADEMICA	2025-10-07 20:13:26.792415	2025-10-07 20:13:26.792415	212
306	Instituto de Investigaciones Jur├¡dicas	3115550203	Calle Morelos 890	Morelia	Centro Hist├│rico	58000	IIJ999999XX7	investigacionjuridica@prueba.edu.mx	\N	ACADEMICA	2025-10-07 20:13:26.792415	2025-10-07 20:13:26.792415	212
301	Direcci├│n de Recursos Humanos	3115550102	Edificio Administrativo, Piso 2	Morelia	Ciudad Universitaria	58000	DRH999999XX2	recursoshumanos@prueba.edu.mx	12	ADMINISTRATIVA	2025-10-07 20:13:26.792415	2026-01-27 19:28:05.453615	212
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.users (id, username, email, password, created_at, updated_at, is_deleted, role, reset_token, reset_token_expiration) FROM stdin;
1	Dani Alonso	ing.leonardo.alonso@gmail.com	$2b$12$QPeLHTEQ8E5F8brU2jJiU.Op8ohio30P4Vs/pc2fZeNBbYF.XFE9.	2025-06-02 20:42:43.543755	2025-06-02 20:42:43.543763	f	ADMIN	\N	\N
3	Contraloria Umsnh	contraloria@umich.mx	$2b$12$YSN/jFQNSjcTZjBBPguhK.KORGY6gzB80G0VpurGKMXMlvWcWqi8.	2025-06-05 17:55:00.614776	2025-06-05 17:55:00.615112	f	ADMIN	\N	\N
4	Leo Alonso	alonsoledesmal@gmail.com	$2b$12$wp8y5FEPlRjf7d4i05KBk.18o4rcMiN.oTMzSg.bAckSASdhdy6cG	2025-06-05 18:17:29.923277	2025-06-05 18:17:29.923308	f	USER	\N	\N
12	Wendy Diaz	wendy.diaz@umich.mx	$2b$12$/uIjgsFa3yA1lSf2F70NcOOUQJcBNotXsfmx4o0LsL0Wd9sqz3yYy	2025-07-02 20:14:50.558101	2025-07-02 20:14:50.558105	f	USER	\N	\N
13	L├¡a B├írbara Guerrero Vargas	lia.barbara.guerrero@umich.mx	$2b$12$BCv3LrSmmdm90IUDVGVthOMl5geqkHftzQ7eUNrN32RS/fKz7rAt2	2025-07-02 20:23:47.163075	2025-07-02 20:23:47.163081	f	USER	\N	\N
14	Maria Villalon	maria.guadalupe.villalon@umich.mx	$2b$12$qWrMXDHGe2WSq9oXrgyk8ePWptOUO6R4cFQ6fxF547/zK99GTgfCm	2025-07-02 20:42:04.777136	2025-07-02 20:42:04.77714	f	USER	\N	\N
2	Guadalupe Villalon	maria.villalon@umich.mx	$2b$12$1w/AbAN4ohPbOfgEVJCoPOmN5KzDqod5utSvsBptPtJ9oedc2ET9W	2025-06-03 17:29:08.941567	2025-06-03 17:29:08.942387	f	AUDITOR	\N	\N
15	Daniel Alonso	leonardo.alonso@umich.mx	$2b$12$F4mdQET1t9PtM79djrgSAu5Ng.JBo.9xP4ZjaaMofhSPNPI9JhVra	2025-07-04 16:12:42.570195	2025-07-04 16:12:42.570225	f	USER	\N	\N
16	Roberto Gonzalez	roberto.gonzalez@umich.mx	$2b$12$LmNOGRXLl3uykppJI.rQa.MJzEJ3.Gn4xEfxpqh/BkVfoFqSU1Gc2	2025-08-18 20:19:01.307338	2025-08-18 20:19:01.307341	f	USER	\N	\N
17	David Suarez	david.suarez@umich.mx	$2b$12$Dl0qX73zTL2qi/dw3eZp0erRhWDvy19Ir/nojHT3lhKnbwyV1NIxC	2025-08-19 17:29:08.722546	2025-08-19 17:29:08.722594	f	USER	\N	\N
18	Rodrigo Mondrag├│n	rodrigo.mondragon@umich.mx	$2b$12$TwPaALJ5cBUngFdkFE9H0umDnOi1LeAHOsgiYdn6L0IAutUmf/fm6	2025-08-19 18:22:48.959284	2025-08-19 18:22:48.959327	f	USER	\N	\N
19	Rolando Fernandez	rolando.fernandez@umich.mx	$2b$12$95U66VX7TG7GzWS2kAIaaOeYLYKHq8tUwCFt7GIWYADD2Ch6.cL12	2025-08-26 19:55:07.388342	2025-08-26 19:55:07.388481	f	USER	\N	\N
20	Rodolfo Juarez	rodolfo.juarez@umich.mx	$2b$12$bwhvhd1XXt50CvSUsAu9COPookWC9ExdZ6a3VdxtLjMhejw8PtRuS	2025-08-27 17:46:23.263457	2025-08-27 17:46:23.263461	f	USER	\N	\N
5	Leonardo Alonso	leonardo.daniel.alonso@umich.mx	$2b$12$yjNCZefBjOxDNzQkCUMHBeexiUukZqyrKCVuj/LwKhVxuk2NSXoNG	2025-06-09 17:00:23.917744	2026-01-28 20:30:54.096905	f	ADMIN	plfAAzWJgYQBXp2NQCkHkabguhyZ4IBS	\N
\.


--
-- Data for Name: usuarios; Type: TABLE DATA; Schema: public; Owner: user
--

COPY public.usuarios (id, username, email, password, created_at, updated_at, is_deleted, rol_id) FROM stdin;
\.


--
-- Name: acta_entrega_recepcion_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.acta_entrega_recepcion_id_seq', 7, true);


--
-- Name: anexos_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.anexos_id_seq', 14, true);


--
-- Name: posts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.posts_id_seq', 1, false);


--
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.roles_id_seq', 1, false);


--
-- Name: unidades_responsables_id_unidad_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.unidades_responsables_id_unidad_seq', 212, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.users_id_seq', 20, true);


--
-- Name: usuarios_id_seq; Type: SEQUENCE SET; Schema: public; Owner: user
--

SELECT pg_catalog.setval('public.usuarios_id_seq', 1, false);


--
-- Name: acta_entrega_recepcion acta_entrega_recepcion_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.acta_entrega_recepcion
    ADD CONSTRAINT acta_entrega_recepcion_pkey PRIMARY KEY (id);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: anexos anexos_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.anexos
    ADD CONSTRAINT anexos_pkey PRIMARY KEY (id);


--
-- Name: posts posts_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_pkey PRIMARY KEY (id);


--
-- Name: roles roles_nombre_key; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_nombre_key UNIQUE (nombre);


--
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- Name: unidades_responsables unidades_responsables_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.unidades_responsables
    ADD CONSTRAINT unidades_responsables_pkey PRIMARY KEY (id_unidad);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: usuarios usuarios_pkey; Type: CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_pkey PRIMARY KEY (id);


--
-- Name: ix_acta_entrega_recepcion_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_acta_entrega_recepcion_id ON public.acta_entrega_recepcion USING btree (id);


--
-- Name: ix_anexos_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_anexos_id ON public.anexos USING btree (id);


--
-- Name: ix_posts_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_posts_id ON public.posts USING btree (id);


--
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- Name: ix_unidades_responsables_id_unidad; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_unidades_responsables_id_unidad ON public.unidades_responsables USING btree (id_unidad);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- Name: ix_usuarios_email; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_usuarios_email ON public.usuarios USING btree (email);


--
-- Name: ix_usuarios_id; Type: INDEX; Schema: public; Owner: user
--

CREATE INDEX ix_usuarios_id ON public.usuarios USING btree (id);


--
-- Name: ix_usuarios_username; Type: INDEX; Schema: public; Owner: user
--

CREATE UNIQUE INDEX ix_usuarios_username ON public.usuarios USING btree (username);


--
-- Name: acta_entrega_recepcion acta_entrega_recepcion_unidad_responsable_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.acta_entrega_recepcion
    ADD CONSTRAINT acta_entrega_recepcion_unidad_responsable_fkey FOREIGN KEY (unidad_responsable) REFERENCES public.unidades_responsables(id_unidad);


--
-- Name: anexos anexos_acta_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.anexos
    ADD CONSTRAINT anexos_acta_id_fkey FOREIGN KEY (acta_id) REFERENCES public.acta_entrega_recepcion(id);


--
-- Name: anexos anexos_creador_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.anexos
    ADD CONSTRAINT anexos_creador_id_fkey FOREIGN KEY (creador_id) REFERENCES public.users(id);


--
-- Name: anexos anexos_unidad_responsable_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.anexos
    ADD CONSTRAINT anexos_unidad_responsable_id_fkey FOREIGN KEY (unidad_responsable_id) REFERENCES public.unidades_responsables(id_unidad);


--
-- Name: unidades_responsables fk_responsable_usuario; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.unidades_responsables
    ADD CONSTRAINT fk_responsable_usuario FOREIGN KEY (responsable) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- Name: posts posts_owner_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.posts
    ADD CONSTRAINT posts_owner_id_fkey FOREIGN KEY (owner_id) REFERENCES public.users(id);


--
-- Name: unidades_responsables unidades_responsables_responsable_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.unidades_responsables
    ADD CONSTRAINT unidades_responsables_responsable_fkey FOREIGN KEY (responsable) REFERENCES public.users(id);


--
-- Name: unidades_responsables unidades_responsables_unidad_padre_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.unidades_responsables
    ADD CONSTRAINT unidades_responsables_unidad_padre_id_fkey FOREIGN KEY (unidad_padre_id) REFERENCES public.unidades_responsables(id_unidad);


--
-- Name: usuarios usuarios_rol_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: user
--

ALTER TABLE ONLY public.usuarios
    ADD CONSTRAINT usuarios_rol_id_fkey FOREIGN KEY (rol_id) REFERENCES public.roles(id);


--
-- PostgreSQL database dump complete
--

\unrestrict 4gVMnczEZa4qs1vZcgSe4XGxAEoANVouIZlFAsJVVtkDgk1DV7rFX54ybzU5XGM

