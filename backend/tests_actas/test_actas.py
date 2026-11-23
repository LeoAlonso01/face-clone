"""Pruebas aisladas: SQLite o TEST_DATABASE_URL serumich_test_actas_*.

Se ejecutan las funciones reales de main.py sin sus efectos globales de arranque
(Drive, directorios /app, lifespan y conexión a la base configurada).
"""
import ast
import logging
import os
import sys
import types
from pathlib import Path

import pytest
from fastapi import FastAPI, Depends, HTTPException, Request, status, UploadFile, File, Form
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import Session, declarative_base, selectinload
from sqlalchemy.pool import StaticPool

database = types.ModuleType("app.database")
database.Base = declarative_base()
sys.modules["app.database"] = database
from app.models import ActaEntregaRecepcion, Anexos, UnidadResponsable, User, UserRoles
from app.schemas import AnexoDetalleResponse, ActaCreate, ActaResponse, ActaUpdate, ActaVistaPreviaRequest, ActaVistaPreviaResponse, ActaDocumentoResponse
from app.anexo_reportes import detalle_anexo_reporte, registrar_reporte_anexo
from app.actas_service import crear_acta_con_anexos, cargar_acta, preparar_participantes, vista_previa_acta, datos_acta_documento


@pytest.fixture
def engine():
    url = os.getenv("TEST_DATABASE_URL", "sqlite://")
    if url != "sqlite://" and not (make_url(url).database or "").startswith("serumich_test_actas_"):
        pytest.fail("Solo se permiten bases desechables serumich_test_actas_*")
    options = {"connect_args": {"check_same_thread": False}, "poolclass": StaticPool} if url == "sqlite://" else {}
    engine = create_engine(url, **options)
    if url == "sqlite://":
        @event.listens_for(engine, "connect")
        def foreign_keys(connection, _):
            connection.execute("PRAGMA foreign_keys=ON")
    database.Base.metadata.create_all(engine)
    yield engine
    database.Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def setup(engine):
    db = Session(engine)
    actor = User(id=1, username="empleado1", email="actor@example.invalid", password="unused", role=UserRoles.ADMIN)
    other = User(id=4, username="empleado4", email="other@example.invalid", password="unused", role=UserRoles.USER)
    db.add_all([actor, other])
    db.flush()
    db.add_all([UnidadResponsable(id_unidad=212, nombre="Unidad 212"), UnidadResponsable(id_unidad=10, nombre="Unidad 10")])
    db.commit()
    def get_db():
        yield db
    def get_current_user():
        return actor
    app = FastAPI()
    namespace = dict(AnexoDetalleResponse=AnexoDetalleResponse, detalle_anexo_reporte=detalle_anexo_reporte, registrar_reporte_anexo=registrar_reporte_anexo, UploadFile=UploadFile, File=File, Form=Form, app=app, get_db=get_db, get_current_user=get_current_user, Session=Session,
                     User=User, Request=Request, Depends=Depends, HTTPException=HTTPException, status=status,
                     ActaCreate=ActaCreate, ActaResponse=ActaResponse, ActaUpdate=ActaUpdate,
                     ActaVistaPreviaRequest=ActaVistaPreviaRequest, ActaVistaPreviaResponse=ActaVistaPreviaResponse, vista_previa_acta=vista_previa_acta,
                     ActaDocumentoResponse=ActaDocumentoResponse, datos_acta_documento=datos_acta_documento,
                     ActaEntregaRecepcion=ActaEntregaRecepcion, selectinload=selectinload,
                     crear_acta_con_anexos=crear_acta_con_anexos, cargar_acta=cargar_acta,
                     preparar_participantes=preparar_participantes, logger=logging.getLogger("actas_test"),
                     create_audit_log=lambda **kwargs: None)
    tree = ast.parse((Path(__file__).resolve().parents[1] / "app/main.py").read_text(encoding="utf-8"))
    functions = [node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in {"read_anexo", "guardar_reporte_anexo", "crear_acta", "read_acta", "update_acta", "previsualizar_acta", "read_acta_documento"}]
    exec(compile(ast.Module(body=functions, type_ignores=[]), "main_actas_endpoints", "exec"), namespace)
    with TestClient(app, raise_server_exceptions=False) as client:
        yield client, db, namespace
    db.close()


def payload(**changes):
    data = dict(unidad_responsable=212, folio="ACTA-TEST", fecha="2026-11-20", comisionado="Comisionado legado",
                entrante="Entrante externo", saliente="Saliente externo")
    data.update(changes)
    return data


def anexo(db, id, creador=1, unidad=212, acta=None, deleted=False):
    db.add(Anexos(id=id, clave="MJ01", creador_id=creador, unidad_responsable_id=unidad,
                  estado="Borrador", datos=[{"dato": "prueba"}], acta_id=acta, is_deleted=deleted))


def test_asocia_diez_sin_tocar_seis_asignados_ni_eliminado_ni_otros(setup):
    client, db, _ = setup
    anterior = ActaEntregaRecepcion(unidad_responsable=212, folio="ANTERIOR", fecha="2026-01-01", comisionado="Anterior")
    db.add(anterior)
    db.flush()
    for id in range(1, 11):
        anexo(db, id)
    for id in range(11, 17):
        anexo(db, id, acta=anterior.id)
    anexo(db, 17, deleted=True)
    anexo(db, 18, creador=4)
    anexo(db, 19, unidad=10)
    db.commit()
    response = client.post("/actas", json=payload(creador_id=4))
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["creador_id"] == 1  # No se confía en un creador enviado por el navegador.
    assert {item["id"] for item in data["anexos"]} == set(range(1, 11))
    db.expire_all()
    assert all(db.get(Anexos, id).acta_id == anterior.id for id in range(11, 17))
    assert all(db.get(Anexos, id).acta_id is None for id in range(17, 20))
    detail = client.get(f'/actas/{data["id"]}')
    assert {item["id"] for item in detail.json()["anexos"]} == set(range(1, 11))
    assert client.post("/actas", json=payload(folio="SEGUNDA")).json()["anexos"] == []


def test_fallo_de_asociacion_revierte_tambien_el_acta(setup, engine):
    client, db, _ = setup
    anexo(db, 1)
    db.commit()
    def fail_after_update(conn, cursor, statement, parameters, context, executemany):
        if statement.lower().startswith("update anexos"):
            raise RuntimeError("Fallo simulado después del UPDATE")
    event.listen(engine, "after_cursor_execute", fail_after_update)
    try:
        assert client.post("/actas", json=payload()).status_code == 500
    finally:
        event.remove(engine, "after_cursor_execute", fail_after_update)
    with Session(engine) as check:
        assert check.query(ActaEntregaRecepcion).count() == 0
        assert check.get(Anexos, 1).acta_id is None


def test_persistencia_participantes_y_oficios_incluye_externos(setup):
    client, db, _ = setup
    data = payload(comisionados=[1], comisiones=[
        {"usuario_id": 1, "nombre": "Nombre completo corregido", "mismo_oficio": True, "oficio_comision": "IGNORAR"},
        {"usuario_id": None, "nombre": "Comisionada externa", "mismo_oficio": False, "oficio_comision": "EXT-2", "fecha_oficio_comision": "2026-11-19"},
    ], oficio_comision="COM-1", fecha_oficio_comision="2026-11-20", entrante_id=None, saliente_id=4, estado="Borrador")
    response = client.post("/actas", json=data)
    assert response.status_code == 201, response.text
    saved = response.json()
    assert saved["comisionado"] == "Nombre completo corregido, Comisionada externa"
    assert saved["comisiones"][0]["oficio_comision"] == "COM-1"
    assert saved["comisiones"][1]["oficio_comision"] == "EXT-2"
    assert saved["saliente_id"] == 4
    db.expire_all()
    reread = client.get(f'/actas/{saved["id"]}').json()
    assert reread["comisiones"] == saved["comisiones"]
    updated = client.put(f'/actas/{saved["id"]}', json={"oficio_comision": "COM-3"})
    assert updated.status_code == 200, updated.text
    assert updated.json()["comisiones"][0]["oficio_comision"] == "COM-3"
    assert updated.json()["comisiones"][1]["oficio_comision"] == "EXT-2"


@pytest.mark.parametrize("changes,status_code", [
    ({"unidad_responsable": 999}, 400),
    ({"comisiones": [{"usuario_id": None, "nombre": "   "}]}, 422),
    ({"comisionados": [4], "comisiones": [{"usuario_id": 4, "nombre": "Usuario regular"}]}, 400),
    ({"entrante_id": 999}, 400),
    ({"comisionados": [1], "comisiones": []}, 400),
])
def test_rechaza_datos_invalidos_sin_crear_acta(setup, changes, status_code):
    client, db, _ = setup
    data = payload()
    data.update(changes)
    assert client.post("/actas", json=data).status_code == status_code
    assert db.query(ActaEntregaRecepcion).count() == 0


def test_folio_repetido_no_reclama_anexos(setup):
    client, db, _ = setup
    assert client.post("/actas", json=payload()).status_code == 201
    anexo(db, 1)
    db.commit()
    assert client.post("/actas", json=payload()).status_code == 400
    assert db.get(Anexos, 1).acta_id is None


def test_fallo_auditoria_no_impide_retornar_acta_y_anexos(setup):
    client, db, namespace = setup
    anexo(db, 1)
    db.commit()
    def fail(**kwargs):
        raise RuntimeError("Fallo auditoría")
    namespace["create_audit_log"] = fail
    response = client.post("/actas", json=payload())
    assert response.status_code == 201, response.text
    assert [item["id"] for item in response.json()["anexos"]] == [1]


def test_dos_creaciones_concurrentes_no_reasignan_anexos(setup, engine):
    if engine.dialect.name != "postgresql":
        pytest.skip("La prueba de concurrencia requiere PostgreSQL")
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    _, db, _ = setup
    for id in range(1, 11):
        anexo(db, id)
    db.commit()
    barrier = Barrier(2)
    def crear(folio):
        with Session(engine) as session:
            barrier.wait(timeout=10)
            return crear_acta_con_anexos(session, ActaCreate(**payload(folio=folio)), 1)[1]
    with ThreadPoolExecutor(max_workers=2) as pool:
        counts = list(pool.map(crear, ["CONCURRENTE-1", "CONCURRENTE-2"]))
    assert sorted(counts) == [0, 10]
    db.expire_all()
    assert len({item.acta_id for item in db.query(Anexos).all()}) == 1


def test_migracion_aditiva_preserva_actas_y_anexos_y_puede_repetirse(setup, engine):
    if engine.dialect.name != "postgresql":
        pytest.skip("La migración requiere PostgreSQL")
    client, db, _ = setup
    saved = client.post("/actas", json=payload()).json()
    anexo(db, 1, acta=saved["id"])
    db.commit()
    # Simular las columnas del esquema anterior en esta base desechable.
    with engine.begin() as connection:
        for name in ("creador_id", "entrante_id", "saliente_id", "comisiones", "comisionados"):
            connection.execute(text(f"ALTER TABLE acta_entrega_recepcion DROP COLUMN {name}"))
    sql = (Path(__file__).resolve().parents[1] / "migrations/005_actas_participantes.sql").read_text(encoding="utf-8")
    for _ in range(2):
        with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as connection:
            connection.exec_driver_sql(sql)
    db.expire_all()
    acta = db.get(ActaEntregaRecepcion, saved["id"])
    assert acta.comisionado == "Comisionado legado"
    assert acta.creador_id is None
    assert acta.comisiones == []
    assert db.get(Anexos, 1).acta_id == saved["id"]


def test_preview_es_solo_lectura_y_confirma_los_mismos_anexos(setup):
    client, db, _ = setup
    anexo(db, 1)
    anexo(db, 2, creador=4)
    anexo(db, 3, unidad=10)
    anexo(db, 4, deleted=True)
    db.commit()
    result = client.post("/actas/vista-previa", json={"unidad_responsable": 212, "creador_id": 4})
    assert result.status_code == 200, result.text
    preview = result.json()
    assert preview["total"] == 1
    assert preview["anexos"] == [{"id": 1, "clave": "MJ01", "estado": "Borrador", "fecha_creacion": preview["anexos"][0]["fecha_creacion"], "filas": 1}]
    assert db.query(ActaEntregaRecepcion).count() == 0
    assert db.get(Anexos, 1).acta_id is None
    created = client.post("/actas", json=payload(anexos_revision=preview["anexos_revision"]))
    assert created.status_code == 201, created.text
    assert [item["id"] for item in created.json()["anexos"]] == [1]


@pytest.mark.parametrize("change", ["estado", "datos", "nuevo", "eliminado", "asociado"])
def test_preview_desactualizada_rechaza_creacion_y_permite_revisar(setup, change):
    client, db, _ = setup
    anexo(db, 1)
    db.commit()
    revision = client.post("/actas/vista-previa", json={"unidad_responsable": 212}).json()["anexos_revision"]
    item = db.get(Anexos, 1)
    existing_count = 0
    if change == "estado":
        item.estado = "Completado"
    elif change == "datos":
        item.datos = [{"dato": "actualizado el mismo día"}]
    elif change == "nuevo":
        anexo(db, 2)
    elif change == "eliminado":
        item.is_deleted = True
    else:
        anterior = ActaEntregaRecepcion(unidad_responsable=212, folio="ANTERIOR", fecha="2026-01-01", comisionado="Anterior")
        db.add(anterior)
        db.flush()
        item.acta_id = anterior.id
        existing_count = 1
    db.commit()
    rejected = client.post("/actas", json=payload(anexos_revision=revision))
    assert rejected.status_code == 409, rejected.text
    assert db.query(ActaEntregaRecepcion).count() == existing_count
    nueva = client.post("/actas/vista-previa", json={"unidad_responsable": 212}).json()
    assert nueva["anexos_revision"] != revision
    assert client.post("/actas", json=payload(anexos_revision=nueva["anexos_revision"])).status_code == 201


def test_preview_vacia_y_unidad_inexistente(setup):
    client, _, _ = setup
    assert client.post("/actas/vista-previa", json={"unidad_responsable": 999}).status_code == 400
    result = client.post("/actas/vista-previa", json={"unidad_responsable": 212}).json()
    assert result["total"] == 0 and result["anexos"] == []
    response = client.post("/actas", json=payload(anexos_revision=result["anexos_revision"]))
    assert response.status_code == 201 and response.json()["anexos"] == []


def test_confirmaciones_concurrentes_de_misma_preview_solo_crean_una_acta(setup, engine):
    if engine.dialect.name != "postgresql":
        pytest.skip("La prueba de concurrencia requiere PostgreSQL")
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier
    client, db, _ = setup
    anexo(db, 1)
    db.commit()
    revision = client.post("/actas/vista-previa", json={"unidad_responsable": 212}).json()["anexos_revision"]
    barrier = Barrier(2)
    def confirmar(folio):
        with Session(engine) as session:
            barrier.wait(timeout=10)
            try:
                crear_acta_con_anexos(session, ActaCreate(**payload(folio=folio, anexos_revision=revision)), 1)
                return 201
            except HTTPException as error:
                return error.status_code
    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(confirmar, ["CONFIRMACION-1", "CONFIRMACION-2"])) == [201, 409]
    assert db.query(ActaEntregaRecepcion).count() == 1


def preparar_caso_saliente_16(db):
    db.add(User(id=16, username="EMP0016", email="saliente16@example.invalid", password="unused", role=UserRoles.USER))
    db.add(UnidadResponsable(id_unidad=49, nombre="Unidad 49"))
    db.flush()
    for id, clave in [(54, "MJ01"), (55, "RM01"), (56, "SGC01")]:
        db.add(Anexos(id=id, clave=clave, creador_id=16, unidad_responsable_id=49, datos=[{"prueba": True}], estado="Borrador"))
    anexo(db, 57, creador=1, unidad=49)
    anexo(db, 58, creador=16, unidad=49, deleted=True)
    anexo(db, 59, creador=16, unidad=212)
    db.commit()


def test_admin_asocia_anexos_54_55_56_del_saliente_16_y_unidad_49(setup):
    client, db, _ = setup
    preparar_caso_saliente_16(db)
    response = client.post("/actas/vista-previa", json={"unidad_responsable": 49, "saliente_id": 16})
    assert response.status_code == 200, response.text
    preview = response.json()
    assert preview["anexos_creador_id"] == 16
    assert preview["anexos_origen"] == "saliente"
    assert {item["id"] for item in preview["anexos"]} == {54, 55, 56}
    assert all(item["estado"] == "Borrador" for item in preview["anexos"])
    result = client.post("/actas", json=payload(unidad_responsable=49, saliente_id=16,
        saliente="Nombre completo del saliente", anexos_revision=preview["anexos_revision"]))
    assert result.status_code == 201, result.text
    saved = result.json()
    assert saved["creador_id"] == 1
    assert saved["saliente_id"] == 16
    assert saved["saliente"] == "Nombre completo del saliente"
    assert {item["id"] for item in saved["anexos"]} == {54, 55, 56}
    db.expire_all()
    assert all(db.get(Anexos, id).acta_id is None for id in (57, 58, 59))


def test_saliente_sin_nombre_no_crea_acta_ni_asocia_anexos(setup):
    client, db, _ = setup
    preparar_caso_saliente_16(db)
    result = client.post("/actas", json=payload(unidad_responsable=49, saliente_id=16, saliente=""))
    assert result.status_code == 400
    assert db.query(ActaEntregaRecepcion).count() == 0
    assert db.get(Anexos, 54).acta_id is None


def test_usuario_regular_no_puede_consultar_ni_asociar_anexos_de_otro_saliente(setup):
    client, db, namespace = setup
    preparar_caso_saliente_16(db)
    namespace["app"].dependency_overrides[namespace["get_current_user"]] = lambda: db.get(User, 4)
    assert client.post("/actas/vista-previa", json={"unidad_responsable": 49, "saliente_id": 16}).status_code == 403
    assert client.post("/actas", json=payload(unidad_responsable=49, saliente_id=16)).status_code == 403
    assert db.get(Anexos, 54).acta_id is None


def test_cambiar_saliente_despues_de_preview_exige_reconfirmar(setup):
    client, db, _ = setup
    preparar_caso_saliente_16(db)
    preview = client.post("/actas/vista-previa", json={"unidad_responsable": 49, "saliente_id": 16}).json()
    result = client.post("/actas", json=payload(unidad_responsable=49, saliente_id=None, anexos_revision=preview["anexos_revision"]))
    assert result.status_code == 409
    assert db.query(ActaEntregaRecepcion).count() == 0


def test_documento_pdf_recupera_datos_vigentes_y_solo_anexos_asociados_activos(setup):
    client, db, _ = setup
    saved = client.post("/actas", json=payload()).json()
    acta_id = saved["id"]
    anexo(db, 1, acta=acta_id)
    anexo(db, 2, acta=acta_id, deleted=True)
    anexo(db, 3)
    db.commit()
    first = client.get(f"/actas/{acta_id}/datos-pdf")
    assert first.status_code == 200, first.text
    assert first.json()["unidad_nombre"] == "Unidad 212"
    assert [item["id"] for item in first.json()["anexos"]] == [1]
    assert first.json()["saliente"] == "Saliente externo"
    acta = db.get(ActaEntregaRecepcion, acta_id)
    acta.saliente = "Nombre actualizado en base de datos"
    acta.observaciones = "Observaciones guardadas"
    acta.comisiones = [{"usuario_id": None, "nombre": "Comisionada externa", "mismo_oficio": False,
                        "oficio_comision": "EXT-03", "fecha_oficio_comision": "2026-11-21"}]
    db.commit()
    second = client.get(f"/actas/{acta_id}/datos-pdf").json()
    assert second["saliente"] == acta.saliente
    assert second["observaciones"] == acta.observaciones
    assert second["comisiones"][0]["oficio_comision"] == "EXT-03"
    assert db.get(Anexos, 3).acta_id is None
    assert client.get("/actas/999999/datos-pdf").status_code == 404


def pdf_reporte(revision, paginas=3):
    import io
    from pypdf import PdfWriter
    writer = PdfWriter()
    for _ in range(paginas):
        writer.add_blank_page(width=612, height=792)
    writer.add_metadata({"/Subject": revision})
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_reporte_cuenta_pdf_y_conserva_revision_y_nombres(setup):
    client, db, _ = setup
    anexo(db, 1)
    db.commit()
    detalle = client.get('/anexos/1').json()
    assert detalle['unidad_responsable_nombre'] == 'Unidad 212'
    assert detalle['creador_nombre'] == 'empleado1'
    original = db.get(Anexos, 1).actualizado_en
    response = client.post('/anexos/1/reporte', data={'revision': detalle['reporte_revision_actual'], 'formato': detalle['reporte_formato_actual']}, files={'file': ('reporte.pdf', pdf_reporte(detalle['reporte_revision_actual']), 'application/pdf')})
    assert response.status_code == 200, response.text
    saved = response.json()
    assert saved['fojas_reporte'] == 3 and saved['reporte_vigente'] is True
    assert saved['reporte_revision_actual'] == detalle['reporte_revision_actual']
    assert db.get(Anexos, 1).actualizado_en == original
    created = client.post('/actas', json=payload()).json()
    documento = client.get(f"/actas/{created['id']}/datos-pdf").json()
    assert documento['anexos'][0]['fojas_reporte'] == 3
    db.get(Anexos, 1).datos = [{'dato': 'cambio'}]
    db.commit()
    assert client.get('/anexos/1').json()['reporte_vigente'] is False
    documento = client.get(f"/actas/{created['id']}/datos-pdf").json()
    assert documento['anexos'][0]['fojas_reporte'] is None
    response = client.post('/anexos/1/reporte', data={'revision': detalle['reporte_revision_actual'], 'formato': detalle['reporte_formato_actual']}, files={'file': ('reporte.pdf', pdf_reporte(detalle['reporte_revision_actual']), 'application/pdf')})
    assert response.status_code == 409


@pytest.mark.parametrize('tipo', ['otro_pdf', 'invalido', 'sin_permiso'])
def test_reporte_rechaza_archivos_y_actores_incorrectos(setup, tipo):
    client, db, namespace = setup
    anexo(db, 1)
    db.commit()
    detalle = client.get('/anexos/1').json()
    contenido = pdf_reporte('otra-revision') if tipo == 'otro_pdf' else b'no es pdf'
    if tipo == 'sin_permiso':
        namespace['app'].dependency_overrides[namespace['get_current_user']] = lambda: db.get(User, 4)
    response = client.post('/anexos/1/reporte', data={'revision': detalle['reporte_revision_actual'], 'formato': detalle['reporte_formato_actual']}, files={'file': ('reporte.pdf', contenido, 'application/pdf')})
    assert response.status_code == (403 if tipo == 'sin_permiso' else 422), response.text
    assert db.get(Anexos, 1).fojas_reporte is None
