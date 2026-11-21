-- Ejecutar una vez antes de desplegar el backend actualizado.
-- No reasigna anexos ni modifica los nombres/oficios de actas existentes.
BEGIN;
ALTER TABLE public.acta_entrega_recepcion
    ADD COLUMN IF NOT EXISTS creador_id INTEGER REFERENCES public.users(id),
    ADD COLUMN IF NOT EXISTS entrante_id INTEGER REFERENCES public.users(id),
    ADD COLUMN IF NOT EXISTS saliente_id INTEGER REFERENCES public.users(id),
    ADD COLUMN IF NOT EXISTS comisionados JSON NOT NULL DEFAULT '[]'::json,
    ADD COLUMN IF NOT EXISTS comisiones JSON NOT NULL DEFAULT '[]'::json;

-- Un acta histórica no permite deducir su creador con seguridad; conservar NULL.
CREATE INDEX IF NOT EXISTS ix_anexos_pendientes_acta_creador_unidad
    ON public.anexos (creador_id, unidad_responsable_id)
    WHERE (acta_id IS NULL OR acta_id = 0) AND is_deleted IS NOT TRUE;
COMMIT;
