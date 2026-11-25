# Actas: lugar e identificación de funcionarios

Aplicar `007_actas_datos_funcionarios.sql` antes de desplegar este backend.
Agrega siete columnas opcionales sin defaults ni actualizaciones de filas.
Puede ejecutarse nuevamente; no cambia valores previos ni vínculos de anexos.

Los campos son `lugar_acta`, `ine_saliente`, `domicilio_saliente`,
`telefono_saliente`, `nombramiento_saliente`, `asignacion_saliente` y
`asignado_por_saliente`. Los del entrante mantienen sus nombres actuales.
INE se conserva como texto para respetar ceros iniciales.

POST /actas y PUT /actas/{id} aceptan estos campos. Las respuestas de creación,
consulta, edición y GET /actas/{id}/datos-pdf los incluyen. La edición se permite en Pendiente, Revisión y Borrador (compatibilidad).
Completada queda cerrada. ADMIN y AUDITOR pueden editar; USER solo actas propias.
Con anexos activos asociados se conservan la unidad y la cuenta del saliente.

Los clientes anteriores pueden omitirlos; las actas históricas los conservan
como NULL hasta que se editen expresamente. No se rellena Morelia ni se deducen
datos de identificación. No se elimina fecha_nombramiento histórica.
La modificación de la plantilla PDF corresponde a otra etapa.

Pruebas: `python -m pytest tests_actas -q` usa una base SQLite en memoria;
la prueba de la migración usa únicamente TEST_DATABASE_URL serumich_test_actas_*.
