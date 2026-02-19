from backend.app.database import engine
from sqlalchemy import text

print('engine.url =', engine.url)
with engine.connect() as conn:
    rows = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename"))
    print('public tables:')
    for r in rows:
        print(' -', r[0])
    # show counts for cargos and user_cargo_historial if present
    for t in ('cargos','user_cargo_historial'):
        val = conn.execute(text(f"SELECT to_regclass('public.{t}')")).scalar()
        print(f"to_regclass({t}) =>", val)
        if val:
            cnt = conn.execute(text(f"SELECT count(*) FROM {t}" )).scalar()
            print(f"  rows in {t}: {cnt}")
