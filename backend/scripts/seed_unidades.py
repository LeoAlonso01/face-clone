"""Script de seed para poblar la tabla `unidades_responsables` usando los models de la app.

Cómo usar:

# Desde la máquina (con DATABASE_URL apuntando a tu Postgres del docker-compose):
# export DATABASE_URL='postgresql://user:password@localhost:5433/facebook_clone'
# python backend/scripts/seed_unidades.py

# O dentro del contenedor backend:
# docker compose exec backend python backend/scripts/seed_unidades.py

El script: 
- parsea `backend/app/database.sql` buscando INSERTs en `unidades_responsables`
- extrae nombre, municipio, nivel y referencia a unidad padre (si hay alias como (SELECT id FROM rectoria) o (SELECT id FROM secretaria_particular))
- usa los modelos (UnidadResponsable) para insertar las filas en la DB y resolver padres por nombre
"""

import re
import os
import sys
from sqlalchemy.orm import Session

# Ajustar PYTHONPATH en caso necesario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database import SessionLocal, engine
from app.models import UnidadResponsable

SQL_FILE = os.path.join(os.path.dirname(__file__), '..', 'app', 'database.sql')


def read_sql():
    with open(SQL_FILE, 'r', encoding='utf-8') as f:
        return f.read()


def extract_aliases(sql_text):
    # Busca líneas como: secretaria_particular AS (SELECT id FROM unidades_responsables WHERE nombre = 'Secretaría Particular'),
    aliases = {}
    pattern = re.compile(r"(\w+)\s+AS\s+\(SELECT\s+id\s+FROM\s+unidades_responsables\s+WHERE\s+nombre\s*=\s*'([^']+)'\)", re.IGNORECASE)
    for m in pattern.finditer(sql_text):
        alias = m.group(1)
        name = m.group(2)
        aliases[alias] = name
    # Rectoria may be referenced as rectoria alias defined earlier: WITH rectoria AS (SELECT id FROM unidades_responsables WHERE nombre = 'Rectoría')
    m = re.search(r"WITH\s+rectoria\s+AS\s+\(SELECT\s+id\s+FROM\s+unidades_responsables\s+WHERE\s+nombre\s*=\s*'([^']+)'\)", sql_text, re.IGNORECASE)
    if m:
        aliases['rectoria'] = m.group(1)
    return aliases


def extract_inserts(sql_text):
    # Encuentra bloques INSERT INTO unidades_responsables (...) VALUES (...); (puede haber múltiples bloques)
    inserts = []
    # Pattern que captura el bloque VALUES (...) hasta punto y coma
    block_pattern = re.compile(r"INSERT\s+INTO\s+unidades_responsables[\s\S]*?VALUES\s*(\([\s\S]*?\));", re.IGNORECASE)
    # Este patrón captura múltiples tuplas dentro del paréntesis final (para el primer bloque)
    # Buscaremos bloques y luego extraeremos todas las tuplas
    # Alternativamente consideraremos bloques con VALUES followed by ( ... ), ( ... ), ... ;
    blocks = re.findall(r"INSERT\s+INTO\s+unidades_responsables[\s\S]*?VALUES\s*(\([\s\S]*?\));", sql_text, flags=re.IGNORECASE)
    # Pero el regex anterior solo captura el primer paren; mejor capturar desde VALUES hasta ;
    blocks = re.findall(r"INSERT\s+INTO\s+unidades_responsables[\s\S]*?VALUES\s*(.*?);", sql_text, flags=re.IGNORECASE)
    tuples = []
    for block in blocks:
        # block puede tener paréntesis y múltiples tuplas separadas por ,\n
        # normalize newlines
        b = block.strip()
        # remove trailing commas and whitespace
        # We want to split on ),\s*\n\s*(?=\() or '),\n  (' patterns
        # But be robust: split by '),\n' then add back ')'
        parts = re.split(r"\),\s*\n", b)
        for i, part in enumerate(parts):
            p = part.strip()
            if not p:
                continue
            if not p.endswith(')'):
                p = p + ')'  # add if trimmed
            tuples.append(p)
    return tuples


def parse_tuple(t):
    # Expected basic forms: ('Name', 'Morelia', 1, (SELECT id FROM rectoria), CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    # We'll extract the first two strings, an integer, and optionally a parent reference
    name_m = re.search(r"^\s*\'([^']+)\'\s*,", t)
    if not name_m:
        return None
    name = name_m.group(1).strip()
    # municipio
    mun_m = re.search(r"^\s*\'[^']+\'\s*,\s*\'([^']*)\'\s*,", t)
    municipio = mun_m.group(1).strip() if mun_m else None
    # nivel
    nivel_m = re.search(r"\'[^']*'\s*,\s*'[^']*'\s*,\s*(\d+)", t)
    nivel = int(nivel_m.group(1)) if nivel_m else None
    # parent alias like (SELECT id FROM rectoria)
    parent_m = re.search(r"\(\s*SELECT\s+id\s+FROM\s+(\w+)\s*\)", t, re.IGNORECASE)
    parent_alias = parent_m.group(1) if parent_m else None
    return {'nombre': name, 'municipio': municipio, 'nivel': nivel, 'parent_alias': parent_alias}


def seed():
    sql_text = read_sql()
    aliases = extract_aliases(sql_text)

    # extract tuples robustly scanning for occurrences like ('Name','Municipio', 1, (SELECT id FROM alias) ... )
    tuple_pattern = re.compile(r"\(\s*'([^']+)'\s*,\s*'([^']*)'\s*,\s*(\d+)(?:\s*,\s*\(SELECT\s+id\s+FROM\s+(\w+)\s*\))?", re.IGNORECASE)
    tuples = []
    for m in tuple_pattern.finditer(sql_text):
        name = m.group(1)
        municipio = m.group(2)
        nivel = int(m.group(3))
        parent_alias = m.group(4)
        tuples.append({'nombre': name, 'municipio': municipio, 'nivel': nivel, 'parent_alias': parent_alias})

    print(f"Found {len(tuples)} tuples and {len(aliases)} aliases")

    # Ensure tables exist (create from models)
    from app.database import Base
    print('Ensuring DB tables exist...')
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Create root Rectoría if not exists
        root_name = 'Rectoría'
        root = db.query(UnidadResponsable).filter(UnidadResponsable.nombre == root_name).first()
        if not root:
            root = UnidadResponsable(nombre=root_name, municipio='Morelia')
            db.add(root)
            db.commit()
            db.refresh(root)
            print('Created root:', root.id_unidad)
        else:
            print('Root exists:', root.id_unidad)

        name_to_id = {root.nombre: root.id_unidad}

        # First pass: insert all tuples without parent or whose parent_alias == 'rectoria'
        pending = []
        for t in tuples:
            parsed = t if isinstance(t, dict) else parse_tuple(t)
            if not parsed:
                continue
            name = parsed['nombre']
            mun = parsed['municipio'] or 'Morelia'
            nivel = parsed['nivel'] if parsed['nivel'] is not None else 1
            parent_alias = parsed['parent_alias']

            if parent_alias is None:
                # no parent referenced; insert with parent None
                parent_id = None
            else:
                # resolve alias
                parent_name = aliases.get(parent_alias)
                if parent_name == root_name:
                    parent_id = root.id_unidad
                elif parent_name and parent_name in name_to_id:
                    parent_id = name_to_id[parent_name]
                else:
                    # postpone
                    pending.append((name, mun, nivel, parent_alias))
                    continue

            # Create or skip if exists
            existing = db.query(UnidadResponsable).filter(UnidadResponsable.nombre == name).first()
            if existing:
                name_to_id[name] = existing.id_unidad
                continue
            new = UnidadResponsable(nombre=name, municipio=mun, tipo_unidad=None, unidad_padre_id=parent_id)
            db.add(new)
            db.commit()
            db.refresh(new)
            name_to_id[name] = new.id_unidad
            print('Inserted:', name, 'id=', new.id_unidad, 'parent=', parent_id)

        # Resolve pending by trying to match parent_alias using aliases map
        if pending:
            print('Resolving pending items:', len(pending))
            for name, mun, nivel, parent_alias in pending:
                parent_name = aliases.get(parent_alias)
                parent_id = name_to_id.get(parent_name)
                existing = db.query(UnidadResponsable).filter(UnidadResponsable.nombre == name).first()
                if existing:
                    continue
                new = UnidadResponsable(nombre=name, municipio=mun, tipo_unidad=None, unidad_padre_id=parent_id)
                db.add(new)
                db.commit()
                db.refresh(new)
                name_to_id[name] = new.id_unidad
                print('Inserted pending:', name, 'id=', new.id_unidad, 'parent_name=', parent_name)

        print('Seeding complete. Total inserted:', len(name_to_id))
    finally:
        db.close()


if __name__ == '__main__':
    seed()
