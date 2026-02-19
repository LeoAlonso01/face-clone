from backend.app.database import engine
from sqlalchemy import text

print('engine.url =', engine.url)
with engine.connect() as conn:
    print("to_regclass cargos =>", conn.execute(text("SELECT to_regclass('public.cargos')")).scalar())
    print("to_regclass user_cargo_historial =>", conn.execute(text("SELECT to_regclass('public.user_cargo_historial')")).scalar())
