BEGIN TRANSACTION READ ONLY;
SELECT 'catalogo' AS tabla, count(*) AS registros FROM anexo_catalogo
UNION ALL SELECT 'configuraciones', count(*) FROM usuario_anexo_config
UNION ALL SELECT 'permisos', count(*) FROM usuario_anexo_permiso
UNION ALL SELECT 'historial', count(*) FROM usuario_anexo_historial;
SELECT count(*) AS permisos_huerfanos FROM usuario_anexo_permiso p
LEFT JOIN usuario_anexo_config c ON c.user_id=p.user_id
LEFT JOIN anexo_catalogo a ON a.clave=p.clave WHERE c.user_id IS NULL OR a.clave IS NULL;
SELECT count(*) AS configuraciones_sin_historial FROM usuario_anexo_config c
LEFT JOIN usuario_anexo_historial h ON h.user_id=c.user_id AND h.revision=c.revision WHERE h.id IS NULL;
COMMIT;
