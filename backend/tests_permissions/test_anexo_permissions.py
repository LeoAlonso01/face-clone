"""Integration tests against a disposable PostgreSQL database, never the configured app DB.

TEST_DATABASE_URL must name a database starting with serumich_test_permisos_.
Run from /app: python -m pytest tests_permissions -q
"""
import os
import pytest
from sqlalchemy import create_engine, select, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, get_db
from app.auth import create_access_token
from app.models import User, UserRoles, UnidadResponsable, Anexos
from app.anexo_permissions import AnexoCatalogo, AnexoConfig, AnexoPermisoHistorial


@pytest.fixture(scope="module")
def engine():
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip("An isolated TEST_DATABASE_URL is required")
    if not (make_url(url).database or "").startswith("serumich_test_permisos_"):
        pytest.fail("Refusing to run outside the disposable test database")
    engine = create_engine(url)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def setup(engine, monkeypatch):
    monkeypatch.setenv("ANEXOS_PERMISOS_ESTRICTOS", "false")
    connection = engine.connect()
    transaction = connection.begin()
    db = Session(bind=connection, join_transaction_mode="create_savepoint")
    admin = User(username="perm_admin", email="perm_admin@example.invalid", password="unused", role=UserRoles.ADMIN, is_deleted=False)
    user = User(username="perm_user", email="perm_user@example.invalid", password="unused", role=UserRoles.USER, is_deleted=False)
    other = User(username="perm_other", email="perm_other@example.invalid", password="unused", role=UserRoles.USER, is_deleted=False)
    auditor = User(username="perm_auditor", email="perm_auditor@example.invalid", password="unused", role=UserRoles.AUDITOR, is_deleted=False)
    db.add_all([admin, user, other, auditor])
    db.flush()
    unit = UnidadResponsable(nombre="Permisos Test", responsable=user.id)
    db.add(unit)
    for key in ("MJ01", "RH01", "RF01"):
        db.merge(AnexoCatalogo(clave=key, categoria_id="1", categoria="Test", descripcion=key, activo=True))
    db.commit()
    def override_db():
        yield db
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app, raise_server_exceptions=False)
    def headers(actor):
        return {"Authorization": "Bearer " + create_access_token({"sub": actor.username})}
    def save(keys, revision=0, target=None):
        return client.put(f"/permisos-anexos/usuarios/{target or user.id}", headers=headers(admin),
                          json={"revision": revision, "claves": keys, "motivo": "Prueba de permisos"})
    def payload(actor=None, clave="MJ01"):
        return {"creador_id": (actor or user).id, "clave": clave, "estado": "Borrador", "datos": [{"dato": "original"}], "unidad_responsable_id": unit.id_unidad}
    yield client, db, admin, user, other, auditor, headers, save, payload
    client.close()
    app.dependency_overrides.clear()
    db.close()
    transaction.rollback()
    connection.close()


def test_only_admin_can_assign_and_user_can_only_read_self(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    path = f"/permisos-anexos/usuarios/{user.id}"
    assert client.put(path, headers=headers(user), json={"revision": 0, "claves": [], "motivo": "Prueba"}).status_code == 403
    assert client.get(path, headers=headers(other)).status_code == 403
    assert client.get(path).status_code == 401
    assert client.get(path, headers=headers(user)).json()["configurado"] is False


def test_assignment_revisions_and_complete_history(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert save(["MJ01", "MJ01"]).json()["claves"] == ["MJ01"]
    assert save(["RF01"], 1).json()["revision"] == 2
    history = client.get(f"/permisos-anexos/usuarios/{user.id}/historial", headers=headers(admin)).json()
    assert history[0]["anteriores"] == ["MJ01"] and history[0]["nuevas"] == ["RF01"]
    assert history[0]["actor_id"] == admin.id
    assert len(history) == 2


def test_stale_revision_does_not_overwrite_or_add_history(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert save(["MJ01"]).status_code == 200
    assert save(["RF01"], 0).status_code == 409
    assert client.get(f"/permisos-anexos/usuarios/{user.id}", headers=headers(admin)).json()["claves"] == ["MJ01"]
    assert db.query(AnexoPermisoHistorial).filter_by(user_id=user.id).count() == 1


def test_invalid_assignment_is_atomic(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert save(["MJ01"]).status_code == 200
    assert save(["RF01", "NO_EXISTE"], 1).status_code == 422
    assert db.get(AnexoConfig, user.id).revision == 1
    assert db.query(AnexoPermisoHistorial).filter_by(user_id=user.id).count() == 1


def test_database_failure_rolls_back_configuration_and_history(setup, monkeypatch):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert save(["MJ01"]).status_code == 200
    from sqlalchemy import event
    def fail_history(mapper, connection, target):
        raise RuntimeError("simulated history storage failure")
    event.listen(AnexoPermisoHistorial, "before_insert", fail_history)
    try:
        assert save(["RF01"], 1).status_code == 500
    finally:
        event.remove(AnexoPermisoHistorial, "before_insert", fail_history)
    config = client.get(f"/permisos-anexos/usuarios/{user.id}", headers=headers(admin)).json()
    assert config["revision"] == 1 and config["claves"] == ["MJ01"]


def test_allowed_capture_and_direct_api_denial(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    save(["MJ01"])
    assert client.post("/anexos", json=payload(), headers=headers(user)).status_code == 200
    assert client.post("/anexos", json=payload(clave="RF01"), headers=headers(user)).status_code == 403
    assert db.query(Anexos).filter_by(creador_id=user.id).count() == 1


def test_spoofed_creator_is_denied_including_admin(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    for actor in (user, admin):
        assert client.post("/anexos", json=payload(other), headers=headers(actor)).status_code == 403
    assert db.query(Anexos).filter(Anexos.creador_id.in_([user.id, other.id, admin.id])).count() == 0


def test_revocation_preserves_annex_data_and_blocks_open_form(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    save(["MJ01"])
    created = client.post("/anexos", json=payload(), headers=headers(user)).json()
    original = db.get(Anexos, created["id"])
    snapshot = (original.creador_id, original.clave, original.datos, original.unidad_responsable_id, original.acta_id, original.is_deleted)
    assert save([], 1).status_code == 200
    assert client.post("/anexos", json=payload(), headers=headers(user)).status_code == 403
    assert client.put(f'/anexos/{created["id"]}', json={"datos": [{"dato": "changed"}]}, headers=headers(user)).status_code == 403
    original = db.get(Anexos, created["id"], populate_existing=True)
    assert snapshot == (original.creador_id, original.clave, original.datos, original.unidad_responsable_id, original.acta_id, original.is_deleted)
    assert client.get(f'/anexos/{created["id"]}').status_code == 200


def test_other_user_edit_and_creator_change_are_denied(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    created = client.post("/anexos", json=payload(), headers=headers(user)).json()
    path = f'/anexos/{created["id"]}'
    assert client.put(path, json={"datos": []}, headers=headers(other)).status_code == 403
    assert client.put(path, json={"creador_id": admin.id}, headers=headers(admin)).status_code == 403
    assert client.put(path, json={"datos": [{"dato": "admin edit"}]}, headers=headers(admin)).status_code == 200
    assert db.get(Anexos, created["id"], populate_existing=True).creador_id == user.id


def test_changing_key_cannot_bypass_revocation(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    created = client.post("/anexos", json=payload(), headers=headers(user)).json()
    save(["RF01"])
    assert client.put(f'/anexos/{created["id"]}', json={"clave": "RF01"}, headers=headers(user)).status_code == 403


def test_pdf_checks_auth_and_key_before_writing(setup, tmp_path, monkeypatch):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    monkeypatch.setattr("app.main.UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr("app.main.STATIC_DIR", str(tmp_path))
    save(["MJ01"])
    def upload(key, auth):
        return client.post("/pdf", data={"clave": key}, files={"file": ("test.pdf", b"%PDF-test", "application/pdf")}, headers=auth)
    assert upload("RF01", headers(user)).status_code == 403
    assert upload("MJ01", {}).status_code == 401
    assert list(tmp_path.iterdir()) == []
    assert upload("MJ01", headers(user)).status_code == 200
    assert len(list(tmp_path.iterdir())) == 1


def test_pending_user_gradual_and_strict_mode(setup, monkeypatch):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert client.get("/permisos-anexos/mios", headers=headers(user)).json()["sin_restriccion"] is True
    assert client.post("/anexos", json=payload(), headers=headers(user)).status_code == 200
    monkeypatch.setenv("ANEXOS_PERMISOS_ESTRICTOS", "true")
    assert client.post("/anexos", json=payload(), headers=headers(user)).status_code == 403
    assert client.post("/anexos", json=payload(admin), headers=headers(admin)).status_code == 200


def test_auditor_cannot_capture_and_unknown_key_rejected(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert client.post("/anexos", json=payload(auditor), headers=headers(auditor)).status_code == 403
    assert client.post("/anexos", json=payload(clave="NO_EXISTE"), headers=headers(user)).status_code == 422


def test_proposal_does_not_activate_permissions(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    client.post("/anexos", json=payload(), headers=headers(user))
    response = client.get(f"/permisos-anexos/usuarios/{user.id}/propuesta", headers=headers(admin))
    assert response.json()["claves"] == ["MJ01"]
    assert db.get(AnexoConfig, user.id) is None


def test_empty_config_is_confirmed_and_denies_capture(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert save([]).json()["configurado"] is True
    assert client.get("/permisos-anexos/mios", headers=headers(user)).json()["sin_restriccion"] is False
    assert client.post("/anexos", json=payload(), headers=headers(user)).status_code == 403


def test_state_transition_uses_partial_payload_and_checks_revocation(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    save(["MJ01"])
    created = client.post("/anexos", json=payload(), headers=headers(user)).json()
    path = f'/anexos/{created["id"]}'
    assert client.put(path, json={"estado": "Revisión"}, headers=headers(user)).status_code == 200
    save([], 1)
    assert client.put(path, json={"estado": "Completado"}, headers=headers(user)).status_code == 403
    assert db.get(Anexos, created["id"], populate_existing=True).estado == "Revisión"


def test_configured_admin_cannot_capture_unassigned_keys_but_can_manage_permissions(setup):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    assert save(["MJ01"], target=admin.id).status_code == 200
    own = client.get("/permisos-anexos/mios", headers=headers(admin)).json()
    assert own["sin_restriccion"] is False and own["claves"] == ["MJ01"]
    assert client.post("/anexos", json=payload(admin, "RF01"), headers=headers(admin)).status_code == 403
    created = client.post("/anexos", json=payload(admin), headers=headers(admin))
    assert created.status_code == 200
    assert client.put(f'/anexos/{created.json()["id"]}', json={"clave": "RF01"}, headers=headers(admin)).status_code == 403
    assert save(["RF01"]).status_code == 200
    assert client.get("/permisos-anexos/usuarios", headers=headers(admin)).status_code == 200


def test_configured_admin_pdf_denial_does_not_write_files(setup, tmp_path, monkeypatch):
    client, db, admin, user, other, auditor, headers, save, payload = setup
    monkeypatch.setattr("app.main.UPLOAD_DIR", str(tmp_path))
    monkeypatch.setattr("app.main.STATIC_DIR", str(tmp_path))
    assert save([], target=admin.id).status_code == 200
    response = client.post("/pdf", data={"clave": "MJ01"},
        files={"file": ("test.pdf", b"%PDF-test", "application/pdf")}, headers=headers(admin))
    assert response.status_code == 403
    assert list(tmp_path.iterdir()) == []


def test_two_concurrent_first_saves_only_one_succeeds(engine):
    import secrets
    from concurrent.futures import ThreadPoolExecutor
    suffix = secrets.token_hex(5)
    with Session(engine) as db:
        admin = User(username=f"concurrent_admin_{suffix}", role=UserRoles.ADMIN, is_deleted=False)
        user = User(username=f"concurrent_user_{suffix}", role=UserRoles.USER, is_deleted=False)
        db.add_all([admin, user]); db.commit()
        user_id, username = user.id, admin.username
        if db.get(AnexoCatalogo, "MJ01") is None:
            db.add(AnexoCatalogo(clave="MJ01", categoria_id="1", categoria="Test", descripcion="Test", activo=True))
            db.commit()
    def override():
        with Session(engine) as db:
            yield db
    app.dependency_overrides[get_db] = override
    auth = {"Authorization": "Bearer " + create_access_token({"sub": username})}
    try:
        # Do not use TestClient as a context manager: it runs the app lifespan against the normal DB.
        def request(_):
            client = TestClient(app, raise_server_exceptions=False)
            try:
                return client.put(f"/permisos-anexos/usuarios/{user_id}", headers=auth,
                    json={"revision": 0, "claves": ["MJ01"], "motivo": "Concurrent save"}).status_code
            finally: client.close()
        with ThreadPoolExecutor(max_workers=2) as executor:
            assert sorted(executor.map(request, range(2))) == [200, 409]
        with Session(engine) as db:
            assert db.get(AnexoConfig, user_id).revision == 1
            assert db.query(AnexoPermisoHistorial).filter_by(user_id=user_id).count() == 1
    finally:
        app.dependency_overrides.clear()


def test_sql_migration_is_repeatable_and_preserves_existing_data(engine):
    from pathlib import Path
    import secrets
    suffix = secrets.token_hex(5)
    with Session(engine) as db:
        user = User(username=f"migration_{suffix}", role=UserRoles.USER, is_deleted=False)
        db.add(user); db.flush()
        unit = UnidadResponsable(nombre="Migration integrity", responsable=user.id)
        db.add(unit); db.flush()
        db.add(Anexos(clave="MJ01", creador_id=user.id, unidad_responsable_id=unit.id_unidad,
                      datos=[{"dato": "must remain unchanged"}], estado="Borrador", is_deleted=False))
        db.commit()
    def fingerprints():
        with engine.connect() as conn:
            return {table: conn.execute(text(f"SELECT md5(coalesce(jsonb_agg(to_jsonb(t) ORDER BY to_jsonb(t)::text)::text, '')) FROM {table} t")).scalar()
                    for table in ("users", "anexos", "unidades_responsables", "acta_entrega_recepcion")}
    before = fingerprints()
    script = (Path(__file__).parents[1] / "migrations" / "004_anexo_permissions.sql").read_text(encoding="utf-8")
    for _ in range(2):
        raw = engine.raw_connection()
        try:
            with raw.cursor() as cursor: cursor.execute(script)
        finally: raw.close()
        assert fingerprints() == before
