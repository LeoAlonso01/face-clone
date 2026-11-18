"""Explicit PostgreSQL migration runner; defaults to read-only inspection.

Run from backend: python migrations/apply_004.py --database EXPECTED_DB [--apply]
Requires the project's normal database environment. Never logs credentials or rows.
"""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.database import engine

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--database", required=True, help="Expected database name; mismatch aborts")
parser.add_argument("--apply", action="store_true", help="Apply the additive migration")
args = parser.parse_args()


def fingerprints(cursor):
    result = {}
    for table in ("users", "anexos", "unidades_responsables", "acta_entrega_recepcion"):
        # Names are hardcoded, never interpolated from external input.
        cursor.execute(f"SELECT count(*), md5(coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text)::text, '')) FROM {table} t")
        result[table] = cursor.fetchone()
    return result


raw = engine.raw_connection()
try:
    with raw.cursor() as cursor:
        cursor.execute("SELECT current_database()")
        actual = cursor.fetchone()[0]
        if actual != args.database:
            raise SystemExit("Database mismatch. No changes applied.")
        cursor.execute("SELECT current_schema()")
        if cursor.fetchone()[0] != "public":
            raise SystemExit("Expected the public schema. Review search_path before migrating.")
        raw.rollback()
        cursor.execute("BEGIN ISOLATION LEVEL REPEATABLE READ")
        cursor.execute("SET LOCAL lock_timeout = '5s'; SET LOCAL statement_timeout = '60s'")
        before = fingerprints(cursor)
        print("Database:", actual)
        print("Existing row counts:", {table: value[0] for table, value in before.items()})
        if not args.apply:
            raw.rollback()
            print("Read-only inspection. Use --apply after backup and rehearsal.")
        else:
            script = (Path(__file__).parent / "004_anexo_permissions.sql").read_text(encoding="utf-8")
            # Keep all statements and checks inside this verified transaction.
            body = script.replace("BEGIN;", "", 1).rsplit("COMMIT;", 1)[0]
            cursor.execute(body)
            if fingerprints(cursor) != before:
                raise RuntimeError("Existing data changed within the migration; rolling back")
            cursor.execute("SELECT count(*) FROM anexo_catalogo")
            catalog_count = cursor.fetchone()[0]
            raw.commit()
            print("Migration committed. Catalog entries:", catalog_count)
            print("Existing users, annexes, units and actas match their previous fingerprints.")
except BaseException:
    raw.rollback()
    raise
finally:
    raw.close()
    engine.dispose()
