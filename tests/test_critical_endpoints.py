import os
# Use a file-backed sqlite DB for tests to ensure all connections share schema
os.environ['DATABASE_URL'] = 'sqlite:///./test_temp.db'

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import Base, engine, SessionLocal
from backend.app.auth import get_password_hash
from backend.app.models import User, UserRoles, UnidadResponsable, ActaEntregaRecepcion, Anexos
from sqlalchemy.orm import Session
from datetime import date, datetime

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def create_user(db: Session, username: str, email: str, password: str, role=UserRoles.USER):
    # ensure no duplicates from previous test runs
    existing = db.query(User).filter((User.username == username) | (User.email == email)).all()
    for ex in existing:
        db.delete(ex)
    db.commit()

    user = User(username=username, email=email, password=get_password_hash(password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

from backend.app.auth import create_access_token
from enum import Enum

def get_token(username: str, password: str):
    # Generar token JWT directamente para evitar dependencias externas en /token
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    assert user is not None
    access_token = create_access_token(data={
        "sub": user.username,
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
        "role": user.role.value if hasattr(user.role, 'value') else user.role
    })
    return access_token


def test_register_requires_admin():
    db = SessionLocal()
    admin = create_user(db, "admin", "admin@test", "adminpass", role=UserRoles.ADMIN)
    token_admin = get_token("admin", "adminpass")

    # without auth -> 401
    r = client.post("/register", json={"username": "u1", "email": "u1@test", "password": "12345678"})
    assert r.status_code == 401

    # with admin -> success
    r = client.post("/register", headers={"Authorization": f"Bearer {token_admin}"}, json={"username": "u2", "email": "u2@test", "password": "12345678"})
    assert r.status_code == 201
    assert "Usuario registrado exitosamente" in r.json()["message"]


def test_forgot_password_sets_token():
    db = SessionLocal()
    user = create_user(db, "u3", "u3@test", "password123")

    r = client.post("/forgot-password", json={"email": user.email})
    assert r.status_code == 200

    # Verify token and expiration set (refresh session to get latest data)
    db.refresh(user)
    assert user.reset_token is not None
    assert user.reset_token_expiration is not None


def test_assign_responsable_requires_admin_and_works():
    db = SessionLocal()
    admin = create_user(db, "admin2", "admin2@test", "adminpass2", role=UserRoles.ADMIN)
    user = create_user(db, "user1", "user1@test", "pass1234")

    unidad = UnidadResponsable(nombre="Unidad A")
    db.add(unidad)
    db.commit()
    db.refresh(unidad)

    token_admin = get_token("admin2", "adminpass2")
    r = client.put(f"/unidades_responsables/{unidad.id_unidad}/asignar-responsable?usuario_id={user.id}", headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 200
    data = r.json()
    assert data["message"] == "Responsable asignado correctamente"

    # Refresh local session to see DB changes
    db.refresh(unidad)
    unidad_db = db.query(UnidadResponsable).filter(UnidadResponsable.id_unidad == unidad.id_unidad).first()
    assert unidad_db.responsable == user.id


def test_delete_acta_requires_admin():
    db = SessionLocal()
    admin = create_user(db, "admin3", "admin3@test", "adminpass3", role=UserRoles.ADMIN)
    user = create_user(db, "normal", "normal@test", "userpass")

    acta = ActaEntregaRecepcion(unidad_responsable=0, folio="F-1", fecha="2024-01-01", comisionado="X")
    db.add(acta)
    db.commit()
    db.refresh(acta)

    token_user = get_token("normal", "userpass")
    r = client.delete(f"/actas/{acta.id}", headers={"Authorization": f"Bearer {token_user}"})
    assert r.status_code == 403

    token_admin = get_token("admin3", "adminpass3")
    r = client.delete(f"/actas/{acta.id}", headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 200

    acta_db = db.query(ActaEntregaRecepcion).filter(ActaEntregaRecepcion.id == acta.id).first()
    assert acta_db is None


def test_delete_anexo_soft_delete_and_permissions():
    db = SessionLocal()
    admin = create_user(db, "admin4", "admin4@test", "adminpass4", role=UserRoles.ADMIN)
    user = create_user(db, "normal2", "normal2@test", "userpass2")

    anexo = Anexos(clave="A-1", creador_id=user.id, datos=[{"tipo":"contrato"}], estado="ACTIVO", unidad_responsable_id=1, fecha_creacion=datetime.utcnow())
    db.add(anexo)
    db.commit()
    db.refresh(anexo)

    token_user = get_token("normal2", "userpass2")
    r = client.delete(f"/anexos/{anexo.id}", headers={"Authorization": f"Bearer {token_user}"})
    assert r.status_code == 403

    token_admin = get_token("admin4", "adminpass4")
    r = client.delete(f"/anexos/{anexo.id}", headers={"Authorization": f"Bearer {token_admin}"})
    assert r.status_code == 200

    # Refresh and re-query to see DB changes
    db.refresh(anexo)
    anexo_db = db.query(Anexos).filter(Anexos.id == anexo.id).first()
    assert anexo_db.is_deleted is True


def test_create_anexo_requires_auth_and_sets_creator():
    db = SessionLocal()
    user = create_user(db, "creator", "creator@test", "creatorpass")

    # without auth
    r = client.post("/anexos", json={"clave":"C-1","creador_id": user.id, "datos": [{"tipo":"doc"}], "estado":"ACTIVO", "unidad_responsable_id": 1})
    assert r.status_code == 401

    token = get_token("creator", "creatorpass")
    r = client.post("/anexos", headers={"Authorization": f"Bearer {token}"}, json={"clave":"C-1","creador_id": 999, "datos": [{"tipo":"doc"}], "estado":"ACTIVO", "unidad_responsable_id": 1})
    assert r.status_code == 200
    created = r.json()
    assert created["creador_id"] == user.id


def test_read_actas_requires_auth():
    db = SessionLocal()
    user = create_user(db, "reader", "reader@test", "readerpass")

    r = client.get("/actas")
    assert r.status_code == 401

    token = get_token("reader", "readerpass")
    r = client.get("/actas", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200

