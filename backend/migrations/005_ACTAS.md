# Actas: participantes, vista previa y asociación de anexos

Aplicar `005_actas_participantes.sql` antes de desplegar por primera vez estas
columnas. La migración es aditiva e idempotente: no cambia nombres, oficios ni
vínculos existentes. El `creador_id` histórico permanece NULL porque no se puede
deducir con certeza de los anexos.

## Dos identidades diferentes

- `creador_id` del acta: siempre la cuenta autenticada; también es el actor de auditoría.
- `creador_id` del anexo: la cuenta seleccionada en `saliente_id`. Si el saliente
  es una persona sin cuenta (`saliente_id: null`), se utiliza la cuenta autenticada
  y el modal informa expresamente ese origen.

ADMIN y AUDITOR pueden gestionar anexos de otro saliente. USER solo sus propios
anexos. El saliente seleccionado debe ser una cuenta regular activa.

## Vista previa y confirmación

`POST /actas/vista-previa` recibe `{ "unidad_responsable": 49, "saliente_id": 16 }`
con el token habitual. Es de solo lectura. Devuelve unidad, total,
`anexos_revision`, `anexos_creador_id`, `anexos_creador_usuario`, `anexos_origen`
y la lista compacta de anexos (id, clave, estado, fecha y cantidad de filas).

El cliente envía `anexos_revision` al confirmar `POST /actas`. El backend bloquea
los anexos elegibles y compara contenido y estado con esa revisión. Si cambiaron
devuelve 409 sin crear el acta; el cliente actualiza la lista y pide otra
confirmación. Solo se asocian los IDs confirmados.

La creación y asociación se confirman en una transacción. Solo se toman anexos
no eliminados, de la unidad seleccionada, del creador de anexos indicado arriba,
y con `acta_id IS NULL` (o 0 heredado). El UPDATE condicional evita reasignaciones
entre creaciones concurrentes. Si falla, se revierte todo. La respuesta incluye
los anexos asociados. La auditoría se guarda después de esa transacción.

`anexos_revision` es opcional para clientes anteriores y no se guarda en la base.
El frontend no realiza PUTs adicionales para asociar anexos.

## Participantes

`entrante_id`, `saliente_id`, `comisionados` (IDs) y `comisiones` (lista JSON de
`{usuario_id, nombre, mismo_oficio, oficio_comision, fecha_oficio_comision}`)
conservan por separado la cuenta y el nombre que debe aparecer en el acta. Un
externo usa `usuario_id: null`; no se crea una cuenta. El nombre capturado de una
cuenta registrada no se sustituye por su username. Debe capturarse el nombre
completo antes de guardar. Para completar el nombre de un usuario ya seleccionado
se mantiene su ID; la opción de persona sin cuenta lo desvincula explícitamente.

## Pruebas

`python -m pytest tests_actas -q` usa SQLite en memoria por defecto. Para
concurrencia y migración, definir `TEST_DATABASE_URL` con una base PostgreSQL
desechable cuyo nombre empiece con `serumich_test_actas_`. Las pruebas crean y
eliminan tablas únicamente de esa base y rechazan otros nombres. No usan la
conexión de la aplicación, Drive ni su arranque.

La restricción previa del PUT que permite editar únicamente actas en estado
`Borrador` se conserva. La selección del origen por saliente no requiere una
migración adicional.
