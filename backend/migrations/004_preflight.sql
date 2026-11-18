-- Solo lectura. No imprime datos ni contenido de anexos.
BEGIN TRANSACTION READ ONLY;
SELECT current_database(), current_schema(), version();
SELECT table_name, column_name, data_type FROM information_schema.columns
WHERE table_schema='public' AND table_name IN ('users','anexos')
AND column_name IN ('id','creador_id','clave','is_deleted','acta_id') ORDER BY table_name, column_name;
SELECT count(*) AS anexos, count(DISTINCT creador_id) AS creadores,
       count(*) FILTER (WHERE acta_id IS NOT NULL) AS vinculados_acta FROM anexos;
SELECT count(*) AS creadores_huerfanos FROM anexos a LEFT JOIN users u ON u.id=a.creador_id WHERE u.id IS NULL;
SELECT count(*) AS claves_vacias FROM anexos WHERE clave IS NULL OR trim(clave)='';
COMMIT;
