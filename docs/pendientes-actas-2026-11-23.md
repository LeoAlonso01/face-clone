# Pendientes de actas — lunes 23 de noviembre de 2026

Estado: pendientes para la siguiente iteración. No se implementaron firmas ni adjuntos de Drive.

## Avance guardado

- Formulario con buscadores de unidad y usuarios, nombres completos editables y personas sin cuenta.
- Varios comisionados, cada uno con oficio común o propio.
- Asociación atómica de anexos del saliente seleccionado y de la unidad responsable.
- Vista previa con revisión de anexos, categorías y validación de cambios antes de confirmar.
- Vista individual con anexos agrupados por categoría.
- PDF con datos vigentes de la base, roles y fechas corregidos, observaciones, oficios individuales, encabezados, paginación y espacios de firma.
- Visor para escritorio, móvil y tablet con navegación, zoom, impresión y descarga.

## Tareas pendientes

4. [ ] **Capturar cada firma por participante.** Seleccionar entrante, saliente, testigo o comisionado; firmar con dedo, lápiz o ratón; borrar y confirmar. Colocar cada firma en su espacio correspondiente. Referencia: https://developer.mozilla.org/en-US/docs/Web/API/Pointer_events/Using_Pointer_Events
5. [ ] **Conservar el documento firmado.** Guardar PDF original y versión firmada vinculados al acta, con fecha, participantes y huella del archivo. Descargar e imprimir esa misma versión. Cualquier modificación posterior requiere una nueva versión para firmar.
6. [ ] **Conectar la cuenta institucional.** Configurar OAuth web para autorizar `entrega.recepcion@umich.mx`, seleccionar carpeta destino y conservar de forma segura el acceso renovable. Referencia: https://developers.google.com/identity/protocols/oauth2/web-server
7. [ ] **Implementar el modal “Adjuntar archivo”.** Mostrar folio; seleccionar PDF; revisar nombre y tamaño; previsualizar; confirmar subida; indicar progreso y errores.
8. [ ] **Crear un endpoint específico**, por ejemplo `POST /actas/{id}/archivos`, que valide sesión, permisos, acta y archivo antes de subirlo.
9. [ ] **Vincular el archivo con el acta.** Guardar ID de Drive, nombre, fecha, usuario y versión. Conservar versiones anteriores al sustituir el documento.
10. [ ] **Consultar el adjunto dentro de la app.** Mostrar archivos en la vista individual con vista previa y descarga; mantenerlos privados y servir su contenido a través del backend.

## Hallazgos para retomar

- “Adjuntar archivo” continúa como función no implementada en la tabla de actas.
- Hay un servicio previo de Drive y una tabla `resumenes`, pero no una integración final conectada al botón.
- El servicio previo intenta cargar una cuenta de servicio; el archivo local de credenciales corresponde a OAuth de escritorio. Hay que ajustar el flujo a OAuth web.
- No reutilizar las operaciones actuales que hacen público el archivo y transfieren su propiedad como solución de almacenamiento.
- La conexión de Drive disponible durante la revisión correspondía a otra cuenta; no se verificó acceso a la carpeta institucional configurada.
- El endpoint de edición `PUT /actas/{id}` solo permite estado `Borrador`, aunque el formulario ofrece `Pendiente`, `Revisión` y `Completada`. La regla queda sin modificar y requiere una decisión antes de habilitar edición general.

## Ramas de trabajo

- Frontend: `codex/actas-buscadores-comisionados`.
- Backend: `codex/actas-asociacion-anexos`.
- El cambio local previo de `backend/app/database.py` no forma parte de estos commits.
- Producción no se modificó. La migración `backend/migrations/005_actas_participantes.sql` se aplicó y verificó únicamente en desarrollo local.
