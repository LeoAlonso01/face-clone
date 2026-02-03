"""
Tests para endpoints de gestión de contraseñas

Para ejecutar:
    pytest backend/tests/test_password_management.py -v

Requisitos:
    pip install pytest pytest-asyncio httpx
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.database import get_db
from backend.app.models import User, UserRoles, PasswordAuditLog
from backend.app.auth import get_password_hash
from sqlalchemy.orm import Session

client = TestClient(app)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def test_user(db: Session):
    """Crear un usuario de prueba"""
    user = User(
        username="testuser",
        email="test@example.com",
        password=get_password_hash("password123"),
        role=UserRoles.USER,
        is_deleted=False
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_admin(db: Session):
    """Crear un admin de prueba"""
    admin = User(
        username="admin",
        email="admin@example.com",
        password=get_password_hash("admin123"),
        role=UserRoles.ADMIN,
        is_deleted=False
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user):
    """Obtener token de usuario normal"""
    response = client.post(
        "/token",
        data={
            "username": test_user.username,
            "password": "password123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def admin_token(test_admin):
    """Obtener token de admin"""
    response = client.post(
        "/token",
        data={
            "username": test_admin.username,
            "password": "admin123"
        }
    )
    return response.json()["access_token"]


# ============================================================================
# TESTS: CHANGE PASSWORD
# ============================================================================

def test_change_password_success(test_user, user_token):
    """Test exitoso: Usuario cambia su propia contraseña"""
    response = client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "exitosamente" in data["message"]


def test_change_password_wrong_current(test_user, user_token):
    """Test: Contraseña actual incorrecta"""
    response = client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "wrongPassword",
            "new_password": "newPassword456!"
        }
    )
    
    assert response.status_code == 400
    assert "incorrecta" in response.json()["detail"]


def test_change_password_too_short(test_user, user_token):
    """Test: Nueva contraseña muy corta"""
    response = client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "password123",
            "new_password": "short"
        }
    )
    
    assert response.status_code == 422  # Validation error
    # o 400 dependiendo de dónde se valide


def test_change_password_same_as_current(test_user, user_token):
    """Test: Nueva contraseña igual a la actual"""
    response = client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "password123",
            "new_password": "password123"
        }
    )
    
    assert response.status_code == 400
    assert "igual" in response.json()["detail"]


def test_change_password_unauthorized(test_user):
    """Test: Sin token de autenticación"""
    response = client.post(
        f"/users/{test_user.id}/change_password",
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    
    assert response.status_code == 401


def test_change_password_forbidden_other_user(test_user, user_token, db: Session):
    """Test: Usuario intenta cambiar contraseña de otro usuario"""
    # Crear otro usuario
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password=get_password_hash("other123"),
        role=UserRoles.USER,
        is_deleted=False
    )
    db.add(other_user)
    db.commit()
    
    response = client.post(
        f"/users/{other_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "other123",
            "new_password": "newPassword456!"
        }
    )
    
    assert response.status_code == 403
    assert "permisos" in response.json()["detail"]


def test_change_password_admin_can_change_others(test_user, test_admin, admin_token):
    """Test: Admin puede cambiar contraseña de otros usuarios"""
    response = client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True


def test_change_password_user_not_found(user_token):
    """Test: Usuario no existe"""
    response = client.post(
        "/users/99999/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    
    assert response.status_code == 404


# ============================================================================
# TESTS: RESET PASSWORD (ADMIN)
# ============================================================================

def test_reset_password_admin_success(test_user, test_admin, admin_token, db: Session):
    """Test exitoso: Admin resetea contraseña de usuario"""
    response = client.post(
        f"/admin/users/{test_user.id}/reset_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "user123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "reseteada" in data["message"]
    
    # Verificar que se creó el log de auditoría
    audit_log = db.query(PasswordAuditLog).filter(
        PasswordAuditLog.admin_id == test_admin.id,
        PasswordAuditLog.target_user_id == test_user.id,
        PasswordAuditLog.action == "password_reset"
    ).first()
    
    assert audit_log is not None
    assert audit_log.success == True


def test_reset_password_non_admin_forbidden(test_user, user_token):
    """Test: Usuario no-admin intenta resetear contraseña"""
    # Crear otro usuario
    response = client.post(
        "/admin/users/2/reset_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={"new_password": "user123"}
    )
    
    assert response.status_code == 403
    assert "administrador" in response.json()["detail"]


def test_reset_password_unauthorized():
    """Test: Sin token de autenticación"""
    response = client.post(
        "/admin/users/1/reset_password",
        json={"new_password": "user123"}
    )
    
    assert response.status_code == 401


def test_reset_password_user_not_found(admin_token):
    """Test: Usuario objetivo no existe"""
    response = client.post(
        "/admin/users/99999/reset_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "user123"}
    )
    
    assert response.status_code == 404


def test_reset_password_too_short(test_user, admin_token):
    """Test: Nueva contraseña muy corta"""
    response = client.post(
        f"/admin/users/{test_user.id}/reset_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "short"}
    )
    
    assert response.status_code == 422  # Validation error


# ============================================================================
# TESTS: AUDIT LOGS
# ============================================================================

def test_audit_log_created_on_reset(test_user, test_admin, admin_token, db: Session):
    """Test: Verificar que se crea log de auditoría al resetear"""
    # Contar logs antes
    count_before = db.query(PasswordAuditLog).count()
    
    # Resetear contraseña
    client.post(
        f"/admin/users/{test_user.id}/reset_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "user123"}
    )
    
    # Contar logs después
    count_after = db.query(PasswordAuditLog).count()
    
    assert count_after == count_before + 1
    
    # Verificar contenido del log
    log = db.query(PasswordAuditLog).order_by(
        PasswordAuditLog.id.desc()
    ).first()
    
    assert log.admin_id == test_admin.id
    assert log.target_user_id == test_user.id
    assert log.action == "password_reset"
    assert log.success == True


def test_audit_log_created_on_admin_change(test_user, test_admin, admin_token, db: Session):
    """Test: Verificar log cuando admin cambia contraseña de otro usuario"""
    # Cambiar contraseña
    client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    
    # Verificar log
    log = db.query(PasswordAuditLog).filter(
        PasswordAuditLog.action == "password_change",
        PasswordAuditLog.admin_id == test_admin.id,
        PasswordAuditLog.target_user_id == test_user.id
    ).first()
    
    assert log is not None


def test_no_audit_log_when_user_changes_own_password(test_user, user_token, db: Session):
    """Test: NO se crea log cuando usuario cambia su propia contraseña"""
    count_before = db.query(PasswordAuditLog).count()
    
    client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    
    count_after = db.query(PasswordAuditLog).count()
    assert count_after == count_before  # No debería aumentar


# ============================================================================
# TESTS: INTEGRATION
# ============================================================================

def test_password_change_and_login_with_new_password(test_user, user_token):
    """Test de integración: Cambiar contraseña y hacer login con la nueva"""
    # Cambiar contraseña
    response = client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    assert response.status_code == 200
    
    # Intentar login con contraseña antigua (debería fallar)
    response = client.post(
        "/token",
        data={
            "username": test_user.username,
            "password": "password123"
        }
    )
    assert response.status_code == 401
    
    # Login con nueva contraseña (debería funcionar)
    response = client.post(
        "/token",
        data={
            "username": test_user.username,
            "password": "newPassword456!"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_admin_reset_and_user_login(test_user, admin_token):
    """Test: Admin resetea contraseña y usuario puede hacer login"""
    # Admin resetea contraseña
    response = client.post(
        f"/admin/users/{test_user.id}/reset_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "resetedPassword123!"}
    )
    assert response.status_code == 200
    
    # Usuario hace login con nueva contraseña
    response = client.post(
        "/token",
        data={
            "username": test_user.username,
            "password": "resetedPassword123!"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


# ============================================================================
# TESTS: SECURITY
# ============================================================================

def test_password_is_hashed_in_database(test_user, user_token, db: Session):
    """Test: Verificar que la contraseña se almacena hasheada"""
    client.post(
        f"/users/{test_user.id}/change_password",
        headers={"Authorization": f"Bearer {user_token}"},
        json={
            "current_password": "password123",
            "new_password": "newPassword456!"
        }
    )
    
    # Refrescar usuario desde BD
    db.refresh(test_user)
    
    # Verificar que la contraseña NO es texto plano
    assert test_user.password != "newPassword456!"
    # Verificar que empieza con el prefijo de bcrypt
    assert test_user.password.startswith("$2b$")


def test_password_not_in_response(test_user, admin_token):
    """Test: Verificar que la contraseña NO se devuelve en la respuesta"""
    response = client.post(
        f"/admin/users/{test_user.id}/reset_password",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"new_password": "user123"}
    )
    
    data = response.json()
    # Verificar que no hay campo "password" en la respuesta
    assert "password" not in data
    assert "new_password" not in data


# ============================================================================
# CONFTEST (si usas archivo conftest.py separado)
# ============================================================================

# Nota: Este código debería ir en conftest.py
"""
@pytest.fixture(scope="session")
def db():
    # Crear base de datos de prueba
    from backend.app.database import Base, engine
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)
"""
