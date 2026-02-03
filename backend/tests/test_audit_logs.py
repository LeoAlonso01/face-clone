"""
Tests para verificart que se crean audit logs en acciones clave
"""
import pytest
import httpx

BASE_URL = 'http://localhost:8000'


def login(username, password):
    resp = httpx.post(f"{BASE_URL}/token", data={'username': username, 'password': password})
    assert resp.status_code == 200
    return resp.json()['access_token'], resp.json().get('user_id')


def test_create_anexo_generates_audit_log():
    # Login como usuario de pruebas
    token, user_id = login('Leo Alonso', 'user12345')

    # Crear un anexo
    body = {
        'clave': 'TEST-ANEXO',
        'creador_id': user_id,
        'datos': [{'foo': 'bar'}],
        'estado': 'VIGENTE',
        'unidad_responsable_id': 1
    }
    headers = {'Authorization': f'Bearer {token}'}
    resp = httpx.post(f"{BASE_URL}/anexos", json=body, headers=headers)
    assert resp.status_code == 200
    anexo = resp.json()
    assert anexo['clave'] == 'TEST-ANEXO'

    # Consultar audit logs como admin
    admin_token, _ = login('Dani Alonso', 'admin123')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}

    resp2 = httpx.get(f"{BASE_URL}/admin/audit_logs", headers=headers_admin, params={'object_type': 'anexo'})
    assert resp2.status_code == 200
    data = resp2.json()
    assert data['total'] >= 1
    # Buscar la entrada correspondiente
    items = data['items']
    found = any(item['action'] == 'create_anexo' and item['object_id'] == anexo['id'] for item in items)
    assert found, 'No se encontró el registro de auditoría para create_anexo'


def test_create_acta_generates_audit_log():
    # Login como usuario
    token, user_id = login('Leo Alonso', 'user12345')

    import time
    folio = f"ACTA-TEST-{int(time.time())}"
    body = {
        'unidad_responsable': 1,
        'folio': folio,
        'fecha': '2026-02-02',
        'hora': '10:00',
        'comisionado': 'Tester',
        'entrante': 'Entrante'
    }
    headers = {'Authorization': f'Bearer {token}'}
    resp = httpx.post(f"{BASE_URL}/actas", json=body, headers=headers)
    assert resp.status_code == 201
    acta = resp.json()

    # Consultar audit logs como admin
    admin_token, _ = login('Dani Alonso', 'admin123')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    resp2 = httpx.get(f"{BASE_URL}/admin/audit_logs", headers=headers_admin, params={'object_type': 'acta'})
    assert resp2.status_code == 200
    data = resp2.json()
    found = any(item['action'] == 'create_acta' and item['object_id'] == acta['id'] for item in data['items'])
    assert found, 'No se encontró el registro de auditoría para create_acta'


def test_update_anexo_generates_audit_log():
    token, user_id = login('Leo Alonso', 'user12345')
    headers = {'Authorization': f'Bearer {token}'}

    # Crear un anexo
    body = {
        'clave': 'UPD-ANEXO',
        'creador_id': user_id,
        'datos': [{'foo': 'bar'}],
        'estado': 'VIGENTE',
        'unidad_responsable_id': 1
    }
    resp = httpx.post(f"{BASE_URL}/anexos", json=body, headers=headers)
    assert resp.status_code == 200
    anexo = resp.json()

    # Actualizar anexo
    update = {'estado': 'REVISION'}
    resp2 = httpx.put(f"{BASE_URL}/anexos/{anexo['id']}", json=update, headers=headers)
    assert resp2.status_code == 200

    # Verificar audit log
    admin_token, _ = login('Dani Alonso', 'admin123')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    resp3 = httpx.get(f"{BASE_URL}/admin/audit_logs", headers=headers_admin, params={'object_type': 'anexo', 'action': 'update_anexo'})
    assert resp3.status_code == 200
    items = resp3.json()['items']
    assert any(item['action'] == 'update_anexo' and item['object_id'] == anexo['id'] for item in items)


def test_delete_anexo_generates_audit_log():
    token, user_id = login('Leo Alonso', 'user12345')
    headers = {'Authorization': f'Bearer {token}'}

    # Crear un anexo
    body = {
        'clave': 'DEL-ANEXO',
        'creador_id': user_id,
        'datos': [{'foo': 'bar'}],
        'estado': 'VIGENTE',
        'unidad_responsable_id': 1
    }
    resp = httpx.post(f"{BASE_URL}/anexos", json=body, headers=headers)
    assert resp.status_code == 200
    anexo = resp.json()

    # Delete
    resp2 = httpx.delete(f"{BASE_URL}/anexos/{anexo['id']}", headers=headers)
    assert resp2.status_code == 200

    admin_token, _ = login('Dani Alonso', 'admin123')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    resp3 = httpx.get(f"{BASE_URL}/admin/audit_logs", headers=headers_admin, params={'object_type': 'anexo', 'action': 'delete_anexo'})
    assert resp3.status_code == 200
    items = resp3.json()['items']
    assert any(item['action'] == 'delete_anexo' and item['object_id'] == anexo['id'] for item in items)


def test_update_and_delete_acta_generate_audit_logs():
    token, user_id = login('Leo Alonso', 'user12345')
    headers = {'Authorization': f'Bearer {token}'}

    import time
    folio = f"ACTA-TEST-{int(time.time())}"
    body = {
        'unidad_responsable': 1,
        'folio': folio,
        'fecha': '2026-02-02',
        'hora': '10:00',
        'comisionado': 'Tester',
        'entrante': 'Entrante'
    }
    resp = httpx.post(f"{BASE_URL}/actas", json=body, headers=headers)
    assert resp.status_code == 201
    acta = resp.json()

    # Update
    resp2 = httpx.put(f"{BASE_URL}/actas/{acta['id']}", json={'folio': folio + '-REV'}, headers=headers)
    assert resp2.status_code == 200

    # Delete (usar token del usuario que creó el acta)
    resp3 = httpx.delete(f"{BASE_URL}/actas/{acta['id']}", headers=headers)
    assert resp3.status_code == 200

    admin_token, _ = login('Dani Alonso', 'admin123')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}
    r_logs = httpx.get(f"{BASE_URL}/admin/audit_logs", headers=headers_admin, params={'object_type': 'acta'})
    assert r_logs.status_code == 200
    items = r_logs.json()['items']
    assert any(item['action'] == 'update_acta' and item['object_id'] == acta['id'] for item in items)
    assert any(item['action'] == 'delete_acta' and item['object_id'] == acta['id'] for item in items)

