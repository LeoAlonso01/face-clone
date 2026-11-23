-- Solo metadatos del reporte; no almacena archivos ni reasigna anexos.
BEGIN;
ALTER TABLE public.anexos
    ADD COLUMN IF NOT EXISTS fojas_reporte INTEGER CHECK (fojas_reporte > 0),
    ADD COLUMN IF NOT EXISTS reporte_generado_en TIMESTAMPTZ,
    ADD COLUMN IF NOT EXISTS reporte_revision VARCHAR(64),
    ADD COLUMN IF NOT EXISTS reporte_formato VARCHAR(40);
COMMIT;
