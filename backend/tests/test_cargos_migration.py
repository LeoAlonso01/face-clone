import pytest
from sqlalchemy import text

try:
    from app.database import engine, SessionLocal
except Exception:
    from backend.app.database import engine, SessionLocal


def table_exists(conn, name: str) -> bool:
    r = conn.execute(text("SELECT to_regclass(:t)").bindparams(t=name)).scalar()
    return r is not None


def test_migrate_and_rollback_create_tables():
    # run migration
    from backend.scripts.migrate_cargos import migrate, rollback

    migrate()
    with engine.connect() as conn:
        assert table_exists(conn, 'public.cargos')
        assert table_exists(conn, 'public.user_cargo_historial')

    # cleanup
    rollback()
    with engine.connect() as conn:
        assert not table_exists(conn, 'public.cargos')
        assert not table_exists(conn, 'public.user_cargo_historial')


def test_models_insert_and_query(db):
    # use ORM models to insert a cargo and a historial entry (transactional - rolled back by fixture)
    from backend.app.models import Cargo, UserCargoHistorial
    from backend.app.models import User, UnidadResponsable

    # ensure there is at least one user and one unidad_responsable for FK
    # create temporary ones via the session provided by the db fixture
    user = User(username='test_user_cargo', email='test_cargo@example.com', password='x')
    db.add(user)
    db.flush()

    unidad = UnidadResponsable(nombre='Test Unidad')
    db.add(unidad)
    db.flush()

    cargo = Cargo(nombre='Prueba Cargo', descripcion='Descripción prueba')
    db.add(cargo)
    db.flush()

    hist = UserCargoHistorial(cargo_id=cargo.id, user_id=user.id, unidad_responsable_id=unidad.id_unidad)
    db.add(hist)
    db.flush()

    # query back
    fetched = db.query(UserCargoHistorial).filter_by(id=hist.id).one()
    assert fetched.cargo_id == cargo.id
    assert fetched.user_id == user.id
    assert fetched.unidad_responsable_id == unidad.id_unidad


def test_unique_partial_index_prevents_two_active_assignments(db):
    from sqlalchemy.exc import IntegrityError
    # crear cargo, unidad, dos usuarios
    cargo = Cargo(nombre='UniqueTestCargo', descripcion='t')
    unidad = UnidadResponsable(nombre='UniqueTestUnidad')
    u1 = User(username='unique_user1', email='unique1@example.com', password='x')
    u2 = User(username='unique_user2', email='unique2@example.com', password='x')
    db.add_all([cargo, unidad, u1, u2])
    db.flush()

    # insertar asignación activa para u1
    h1 = UserCargoHistorial(cargo_id=cargo.id, user_id=u1.id, unidad_responsable_id=unidad.id_unidad)
    db.add(h1)
    db.flush()

    # intentar insertar otra asignación activa para el mismo (cargo, unidad) debe fallar
    h2 = UserCargoHistorial(cargo_id=cargo.id, user_id=u2.id, unidad_responsable_id=unidad.id_unidad)
    db.add(h2)
    with pytest.raises(IntegrityError):
        db.flush()
