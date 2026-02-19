import httpx
import time

BASE_URL = 'http://localhost:8000'


def login(username, password):
    resp = httpx.post(f"{BASE_URL}/token", data={'username': username, 'password': password})
    assert resp.status_code == 200
    return resp.json()['access_token'], resp.json().get('user_id')


def test_cargos_crud_flow():
    admin_token, _ = login('Dani Alonso', 'admin123')
    headers = {'Authorization': f'Bearer {admin_token}'}

    name = f"TEST-CARGO-{int(time.time())}"
    # Create
    r = httpx.post(f"{BASE_URL}/cargos", json={'nombre': name, 'descripcion': 'desc'}, headers=headers)
    assert r.status_code == 200
    cargo = r.json()
    assert cargo['nombre'] == name

    # Read list
    r2 = httpx.get(f"{BASE_URL}/cargos", headers=headers)
    assert r2.status_code == 200
    assert any(c['id'] == cargo['id'] for c in r2.json())

    # Update
    r3 = httpx.put(f"{BASE_URL}/cargos/{cargo['id']}", json={'nombre': name, 'descripcion': 'updated'}, headers=headers)
    assert r3.status_code == 200
    assert r3.json()['descripcion'] == 'updated'

    # Delete
    r4 = httpx.delete(f"{BASE_URL}/cargos/{cargo['id']}", headers=headers)
    assert r4.status_code == 200

    # Ensure not returned in list / GET
    r5 = httpx.get(f"{BASE_URL}/cargos/{cargo['id']}", headers=headers)
    assert r5.status_code == 404


def test_user_cargo_historial_endpoints():
    admin_token, _ = login('Dani Alonso', 'admin123')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}

    user_token, user_id = login('Leo Alonso', 'user12345')
    headers_user = {'Authorization': f'Bearer {user_token}'}

    # create cargo to assign
    cargo_name = f"HIST-CARGO-{int(time.time())}"
    r = httpx.post(f"{BASE_URL}/cargos", json={'nombre': cargo_name, 'descripcion': 'for historial'}, headers=headers_admin)
    assert r.status_code == 200
    cargo = r.json()

    # assign cargo to user
    payload = {
        'cargo_id': cargo['id'],
        'user_id': user_id,
        'unidad_responsable_id': 1,
        'motivo': 'Prueba'
    }
    r2 = httpx.post(f"{BASE_URL}/user_cargo_historial", json=payload, headers=headers_admin)
    assert r2.status_code == 200
    hist = r2.json()
    assert hist['cargo_id'] == cargo['id']
    assert hist['user_id'] == user_id

    # admin can query by user_id
    r3 = httpx.get(f"{BASE_URL}/user_cargo_historial", params={'user_id': user_id}, headers=headers_admin)
    assert r3.status_code == 200
    items = r3.json()
    assert any(i['id'] == hist['id'] for i in items)

    # user can query their own historial
    r4 = httpx.get(f"{BASE_URL}/user_cargo_historial", params={'user_id': user_id}, headers=headers_user)
    assert r4.status_code == 200
    assert any(i['id'] == hist['id'] for i in r4.json())

    # trying to create another active assignment for same cargo+unidad should fail
    r5 = httpx.post(f"{BASE_URL}/user_cargo_historial", json=payload, headers=headers_admin)
    # API now returns 409 Conflict for duplicate active assignment
    assert r5.status_code == 409


def test_cargos_asignar_desasignar_and_user_includes_current_cargos():
    admin_token, _ = login('Dani Alonso', 'admin123')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}

    user_token, user_id = login('Leo Alonso', 'user12345')
    headers_user = {'Authorization': f'Bearer {user_token}'}

    # crear nuevo cargo
    cargo_name = f"ASSIGN-CARGO-{int(time.time())}"
    r = httpx.post(f"{BASE_URL}/cargos", json={'nombre': cargo_name, 'descripcion': 'for assign'}, headers=headers_admin)
    assert r.status_code == 200
    cargo = r.json()

    # asignar via endpoint /cargos/asignar
    payload = {'cargo_id': cargo['id'], 'user_id': user_id, 'unidad_responsable_id': 1, 'motivo': 'Prueba assign'}
    r2 = httpx.post(f"{BASE_URL}/cargos/asignar", json=payload, headers=headers_admin)
    assert r2.status_code == 200
    hist = r2.json()
    assert hist['cargo_id'] == cargo['id']

    # GET /users/{id} debe incluir cargos_actuales
    r3 = httpx.get(f"{BASE_URL}/users/{user_id}")
    assert r3.status_code == 200
    user = r3.json()
    assert 'cargos_actuales' in user
    assert any(c['cargo']['id'] == cargo['id'] for c in user['cargos_actuales'])

    # desasignar usando hist_id
    r4 = httpx.post(f"{BASE_URL}/cargos/desasignar", json={'hist_id': hist['id']}, headers=headers_admin)
    assert r4.status_code == 200

    # ahora GET /users/{id} no debe contener esa asignación activa
    r5 = httpx.get(f"{BASE_URL}/users/{user_id}")
    assert r5.status_code == 200
    user2 = r5.json()
    assert not any(c['cargo']['id'] == cargo['id'] and c['fecha_fin'] is None for c in user2['cargos_actuales'])


def test_assign_with_real_admin_credentials():
    """Login con 'Dani Alonso' (contraseña proporcionada) y asignar un cargo a 'Leo Alonso'."""
    admin_token, _ = login('Dani Alonso', 'Chumel.052613$')
    headers_admin = {'Authorization': f'Bearer {admin_token}'}

    user_token, user_id = login('Leo Alonso', 'user12345')

    # crear nuevo cargo
    cargo_name = f"REALADMIN-ASSIGN-{int(time.time())}"
    r = httpx.post(f"{BASE_URL}/cargos", json={'nombre': cargo_name, 'descripcion': 'real admin assign test'}, headers=headers_admin)
    assert r.status_code == 200
    cargo = r.json()

    # asignar via endpoint /cargos/asignar
    payload = {'cargo_id': cargo['id'], 'user_id': user_id, 'unidad_responsable_id': 1, 'motivo': 'Asignación por Dani Alonso'}
    r2 = httpx.post(f"{BASE_URL}/cargos/asignar", json=payload, headers=headers_admin)
    assert r2.status_code == 200
    hist = r2.json()
    assert hist['cargo_id'] == cargo['id']

    # GET /users/{id} debe incluir cargos_actuales
    r3 = httpx.get(f"{BASE_URL}/users/{user_id}")
    assert r3.status_code == 200
    user = r3.json()
    assert any(c['cargo']['id'] == cargo['id'] for c in user['cargos_actuales'])

    # desasignar usando hist_id
    r4 = httpx.post(f"{BASE_URL}/cargos/desasignar", json={'hist_id': hist['id']}, headers=headers_admin)
    assert r4.status_code == 200

    # ahora GET /users/{id} no debe contener esa asignación activa
    r5 = httpx.get(f"{BASE_URL}/users/{user_id}")
    assert r5.status_code == 200
    user2 = r5.json()
    assert not any(c['cargo']['id'] == cargo['id'] and c['fecha_fin'] is None for c in user2['cargos_actuales'])
