"""
Tests para el endpoint /admin/audit_logs
"""
import httpx
import time

BASE_URL = 'http://localhost:8000'


def login(username, password):
    resp = httpx.post(f"{BASE_URL}/token", data={'username': username, 'password': password})
    assert resp.status_code == 200
    return resp.json()['access_token'], resp.json().get('user_id')


def test_admin_can_read_audit_logs_with_metadata():
    admin_token, _ = login('Dani Alonso', 'admin123')
    headers = {'Authorization': f'Bearer {admin_token}'}

    # Crear un anexo para generar un log
    user_token, user_id = login('Leo Alonso', 'user12345')
    headers_user = {'Authorization': f'Bearer {user_token}'}
    body = {'clave': f'DOC-{int(time.time())}', 'creador_id': user_id, 'datos': [{'x':1}], 'estado': 'VIGENTE', 'unidad_responsable_id': 1}
    r = httpx.post(f"{BASE_URL}/anexos", json=body, headers=headers_user)
    assert r.status_code == 200
    anexo = r.json()

    # Consultar logs filtrando por object_type=anexo
    resp = httpx.get(f"{BASE_URL}/admin/audit_logs", headers=headers, params={'object_type': 'anexo', 'limit': 10})
    assert resp.status_code == 200
    data = resp.json()
    assert 'total' in data and 'items' in data
    # encontrar el log correspondiente y comprobar metadata
    items = data['items']
    found = None
    for it in items:
        if it['action'] == 'create_anexo' and it['object_id'] == anexo['id']:
            found = it
            break
    assert found is not None
    assert 'metadata' in found and found['metadata'] is not None
    assert found['metadata'].get('clave') == anexo['clave']
