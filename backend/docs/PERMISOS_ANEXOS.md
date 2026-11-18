# Permisos de captura por usuario

## Comportamiento

- ADMIN puede guardar y editar asignaciones, cargar propuestas e inspeccionar historial. Una configuración confirmada también limita su captura; administrar permisos sigue permitido por su rol.
- USER puede capturar únicamente las claves confirmadas para su cuenta. La categoría se deriva del catálogo.
- AUDITOR y cuentas sin rol de captura no pueden crear, modificar ni subir PDF.
- Cada guardado exige motivo, incrementa la revisión y registra la configuración anterior y nueva en la misma transacción.
- Una selección vacía confirmada significa cero permisos. No se confunde con un usuario pendiente de configurar.
- El backend valida POST /anexos, PUT /anexos/{id} y POST /pdf. Los PDF requieren sesión y clave en multipart.
- El creador de una captura nueva debe coincidir con la sesión, incluso para ADMIN. El creador existente no puede cambiarse.
- Solo el creador o ADMIN modifica un anexo. Revocar la clave bloquea cambios, incluido intentar cambiar la clave original por una habilitada.
- La revocación no borra registros, datos, archivos ni vínculos con actas. La consulta del detalle permanece disponible con las reglas existentes. El listado personal y sus exportaciones muestran solo claves asignadas, además de los filtros de unidad e historial. La vista administrativa Anexos por usuario conserva su función de supervisión.
- Las reglas de eliminación siguen siendo independientes: Borrador, sin acta, creador o ADMIN.
- Dos guardados de la misma revisión producen un éxito y un conflicto 409. El segundo administrador debe recargar.
- Si falla el historial, se revierte toda la asignación. Si falla la red tras un guardado, recargar permite verificar su revisión sin sobrescribirla.
- Un PDF autorizado puede quedar sin asociar si el usuario cancela después de subirlo. La limpieza de archivos huérfanos no forma parte de esta implementación.

## Activación gradual y carga inicial

Por defecto `ANEXOS_PERMISOS_ESTRICTOS=false`. Un usuario pendiente conserva captura de claves válidas; guardar su primera configuración activa la restricción para esa cuenta. Revisar configuraciones no activa restricciones para los demás.

1. Entrar con ADMIN a Anexos > Habilitar anexos.
2. Seleccionar un usuario, incluso si no tiene anexos.
3. Usar "Sugerir desde anexos existentes". Recupera claves distintas de sus anexos no eliminados, normaliza RRH a RH y avisa de claves fuera del catálogo. No guarda automáticamente.
4. Ajustar claves o categorías, escribir un motivo y guardar. Una configuración vacía requiere confirmación adicional.
5. Repetir por usuario. Verificar con su sesión USER en otro perfil de navegador.
6. Cuando todas las cuentas hayan sido revisadas, definir `ANEXOS_PERMISOS_ESTRICTOS=true` en el entorno del servicio o .env del backend y reiniciarlo. Los usuarios USER nuevos o pendientes quedan sin captura hasta su asignación. ADMIN sin configuración conserva la excepción administrativa; una vez configurado debe respetar sus claves asignadas incluso en modo estricto.

No se importan automáticamente las asignaciones del prototipo en localStorage. El backend es la autoridad; editar el almacenamiento del navegador no concede permisos.

El catálogo inicial se obtuvo de lib/anexosCatalogo.ts y contiene 68 claves. Hay seis claves del catálogo que actualmente no tienen estructura en lib/estructuraPorClave.ts: EO01, PPA01, PP01, RF10, RF18 y SGC01. Esta tarea no modifica sus formularios. Usar claves con estructura, como MJ01, para la prueba de captura completa.

## Migración sin Docker en un servidor

Ejecutar desde la carpeta backend con el entorno Python y las variables de conexión del servicio. No se necesita Docker. No ejecutar sobre producción sin ensayo previo sobre una copia reciente y respaldo restaurable.

1. Respaldar la base con pg_dump y conservar también los archivos subidos según el procedimiento habitual. Ensayar la restauración en otra base. La migración no modifica los directorios de archivos.
2. Ejecutar migrations/004_preflight.sql en modo lectura. Comprobar esquema public, tipos y creadores huérfanos.
3. Ejecutar `python migrations/apply_004.py --database NOMBRE_REAL`. Sin --apply es inspección de solo lectura.
4. Después del respaldo y ensayo: `python migrations/apply_004.py --database NOMBRE_REAL --apply`.
5. Ejecutar migrations/004_verify.sql. Inmediatamente después de instalar sin asignar usuarios, configuraciones, permisos e historial deben estar vacíos.
6. Publicar backend y frontend coordinadamente: /pdf ahora requiere token y clave. Reiniciar el servicio si corresponde. Mantener modo gradual durante la revisión inicial.

Alternativamente, con psql: `psql --dbname NOMBRE_REAL --set ON_ERROR_STOP=1 --file migrations/004_anexo_permissions.sql`. Configurar host/usuario y autenticación mediante el mecanismo habitual, sin escribir contraseñas en scripts. Esta alternativa ejecuta la misma transacción, pero no el cálculo adicional de huellas del ejecutor Python.

La migración crea solamente anexo_catalogo, usuario_anexo_config, usuario_anexo_permiso y usuario_anexo_historial. No asigna usuarios ni cambia tablas existentes. El catálogo usa ON CONFLICT DO NOTHING para no sobrescribir ajustes existentes. Espera por bloqueos máximo 5 segundos y por sentencia 60 segundos. Un fallo revierte la transacción.

El ejecutor comprueba el nombre de la base y el esquema y compara huellas de users, anexos, unidades_responsables y acta_entrega_recepcion dentro de una transacción REPEATABLE READ antes de confirmar. Es una comprobación adicional; no sustituye respaldo ni revisión del esquema real. El cálculo lee las tablas completas y puede requerir planificar una ventana en bases grandes.

Reversión operativa: volver a la versión anterior de backend y frontend de forma coordinada y conservar las cuatro tablas e historial. No ejecutar DROP ni restaurar toda la base encima de una base que ya recibió nuevas capturas. Cambiar modo estricto a gradual por sí solo NO quita las restricciones de usuarios ya configurados. Para deshacer una asignación concreta, guardar una revisión nueva con las claves anteriores.

## Pruebas manuales de aceptación

Usar una cuenta ADMIN y una USER con unidad activa en perfiles distintos de navegador. Para probar con ADMIN, confirmar primero una configuración: también limita su captura. ADMIN sin configuración conserva la excepción administrativa.

| Caso | Acción | Resultado esperado |
|---|---|---|
| Asignación y captura | ADMIN habilita solo MJ01 al USER, agrega motivo y guarda. USER recarga Nuevo Anexo, carga datos válidos y guarda. | Solo aparecen categorías y claves habilitadas; MJ01 se guarda con el creador USER. Revisión e historial visibles para ADMIN. |
| Revocación con formulario abierto | USER deja un MJ01 sin enviar; ADMIN retira MJ01 y guarda. USER intenta guardar. | El servidor rechaza. El formulario conserva los datos. Un MJ01 creado antes sigue consultable con mismo creador y archivos. |
| Configuración vacía | ADMIN desmarca todas las claves, escribe motivo y guarda. Cancelar la confirmación una vez y después aceptarla. | Cancelar no aplica cambios. Confirmar guarda una configuración vacía; USER ve aviso de cero claves y no puede capturar. |
| Dos administradores | Abrir la misma configuración en dos perfiles ADMIN. Guardar cambios distintos sin recargar la segunda sesión. | El primero guarda; el segundo obtiene conflicto y no sobrescribe. Su selección sigue visible y debe recargar explícitamente. |
| Persistencia y propuesta | Cargar propuesta desde anexos existentes, cambiar de usuario cancelando la advertencia, luego guardar y volver a iniciar sesión. | Propuesta no se aplica hasta guardar; los cambios se conservan al cancelar salida; una configuración guardada se recupera desde el servidor. |
| Carga PDF no autorizada | Elegir una clave permitida, retirar su permiso desde ADMIN y subir un PDF sin recargar la sesión USER. | Mensaje de permiso denegado; no se adjunta el archivo ni se escribe desde esa petición rechazada. |
| Conteo | Crear/completar una clave habilitada y comparar tarjetas con registros propios. Retirar esa clave. | Cuenta claves habilitadas únicas, excluye eliminados; registros históricos siguen existiendo aunque ya no cuenten como meta habilitada. |
| Fallo de red | Interrumpir la conexión al guardar una configuración y luego recuperarla. Recargar la configuración. | No asumir éxito sin confirmación; recuperar la revisión vigente, sin reemplazar automáticamente cambios de otro ADMIN. |

## Pruebas automáticas

- Frontend: `npx jest lib/habilitacionAnexos.test.ts components/HabilitacionAnexos.test.tsx lib/usePermisosAnexos.test.tsx components/PdfUploader.test.tsx --runInBand`.
- Backend: instalar requirements-test.txt en un entorno de pruebas; crear una base PostgreSQL vacía cuyo nombre empiece por serumich_test_permisos_; definir TEST_DATABASE_URL apuntando SOLO a ella; ejecutar desde backend `python -m pytest tests_permissions -q`.
- La suite nueva está fuera de tests/ para no ejecutar las pruebas preexistentes que usan datos del servidor configurado. Rechaza nombres de base que no tengan el prefijo temporal. No usar la base normal como TEST_DATABASE_URL.
- Se prueban permisos administrativos, acceso propio, revocación, autoría, PDF, selección vacía, conflictos de versión, fallo de historial y rollback, modos gradual/estricto, propuestas sin activar, concurrencia real en PostgreSQL y migración repetida con huellas de datos existentes.

## Verificación realizada en local

20 pruebas backend y 15 frontend pasaron. La migración se aplicó sobre la base local tras generar respaldo y se ensayó también sobre una restauración del respaldo. Las huellas de los 19 usuarios, 36 anexos, 220 unidades y 10 actas permanecieron idénticas durante la migración. La instalación inicial no confirmó asignaciones automáticamente. En la verificación posterior, el usuario ID 1 ya tenía una configuración confirmada con 15 claves (revisión 1); se respetó sin modificarla. Una petición real para capturar RF01, no asignada, fue rechazada con 403. Sus 22 anexos propios actuales tienen claves asignadas y permanecen visibles; el filtro no los borra ni modifica.

La página /dashboard/anexos y OpenAPI respondieron HTTP 200 en los servidores locales. Los archivos TypeScript modificados no tienen diagnósticos. La revisión global de tipos sigue afectada por errores previos del proyecto, incluido components/backupComponents/showform.tsx. No se modificó ni desplegó el servidor de producción.
