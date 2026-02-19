-- 003_add_cargos.sql
-- Crea tablas cargos y user_cargo_historial + índices y rollback

-- Up
CREATE TABLE IF NOT EXISTS cargos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(80) NOT NULL UNIQUE,
    descripcion TEXT,
    activo BOOLEAN NOT NULL DEFAULT TRUE,
    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS user_cargo_historial (
    id SERIAL PRIMARY KEY,
    cargo_id INTEGER NOT NULL REFERENCES cargos(id),
    user_id INTEGER NOT NULL REFERENCES users(id),
    unidad_responsable_id INTEGER NOT NULL REFERENCES unidades_responsables(id_unidad),

    fecha_inicio TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    fecha_fin TIMESTAMP WITH TIME ZONE NULL,

    asignado_por_user_id INTEGER REFERENCES users(id) ON DELETE SET NULL,
    motivo TEXT,

    creado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    actualizado_en TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS idx_user_cargo_historial_user_fecha_inicio ON user_cargo_historial(user_id, fecha_inicio DESC);
CREATE INDEX IF NOT EXISTS idx_user_cargo_historial_unidad_fecha_fin ON user_cargo_historial(unidad_responsable_id, fecha_fin);
CREATE INDEX IF NOT EXISTS idx_user_cargo_historial_cargo_fecha_fin ON user_cargo_historial(cargo_id, fecha_fin);

CREATE UNIQUE INDEX IF NOT EXISTS ux_cargo_unidad_activo
    ON user_cargo_historial(cargo_id, unidad_responsable_id)
    WHERE fecha_fin IS NULL AND is_deleted = FALSE;

-- Down
-- (Se usan DROP IF EXISTS para rollback)

-- Rollback statement (usar manualmente en caso de ser necesario)
-- DROP TABLE IF EXISTS user_cargo_historial CASCADE;
-- DROP TABLE IF EXISTS cargos CASCADE;
