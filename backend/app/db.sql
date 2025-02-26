CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL
);

-- Crear la tabla 'posts'
CREATE TABLE posts (
    id SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    owner_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Agregar el campo created_at
ALTER TABLE users
ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Agregar el campo updated_at
ALTER TABLE users
ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Agregar el campo is_deleted
ALTER TABLE users
ADD COLUMN is_deleted BOOLEAN DEFAULT FALSE;

-- Crear una función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Crear el trigger para la tabla users
CREATE TRIGGER update_users_updated_at
BEFORE UPDATE ON users
FOR EACH ROW
EXECUTE FUNCTION update_updated_at_column();

-- Agregar el campo role a la tabla users
ALTER TABLE users
ADD COLUMN role VARCHAR(50) DEFAULT 'user';