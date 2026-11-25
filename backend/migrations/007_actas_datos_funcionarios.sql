-- Aplicar antes de desplegar el backend actualizado.
-- Columnas opcionales: conserva los valores históricos y no reasigna anexos.
BEGIN;
ALTER TABLE public.acta_entrega_recepcion
    ADD COLUMN IF NOT EXISTS lugar_acta VARCHAR NULL,
    ADD COLUMN IF NOT EXISTS ine_saliente VARCHAR NULL,
    ADD COLUMN IF NOT EXISTS domicilio_saliente VARCHAR NULL,
    ADD COLUMN IF NOT EXISTS telefono_saliente VARCHAR NULL,
    ADD COLUMN IF NOT EXISTS nombramiento_saliente VARCHAR NULL,
    ADD COLUMN IF NOT EXISTS asignacion_saliente VARCHAR NULL,
    ADD COLUMN IF NOT EXISTS asignado_por_saliente VARCHAR NULL;
COMMIT;
