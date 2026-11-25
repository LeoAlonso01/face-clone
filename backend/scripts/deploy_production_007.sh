#!/usr/bin/env bash
# Despliegue específico del servidor nativo srvcontraloria, sin Docker.
set -Eeuo pipefail
umask 077
[ "$(hostname -s)" = srvcontraloria ] || { echo 'Servidor incorrecto'; exit 1; }
[ "$(id -un)" = daniel ] || { echo 'Usuario incorrecto'; exit 1; }
repo=/home/daniel/face-clone-migration
respaldo=/home/daniel/serumich-prod-pre007.nGhmmD
revision=2810dc6d28f3eb0122d2ea53b8afd88b9e2a28aa
candidato="$respaldo/candidato"
python="$repo/backend/.venv/bin/python"
api=http://172.16.123.109:8000
archivos=(backend/app/main.py backend/app/models.py backend/app/schemas.py backend/app/actas_service.py backend/app/anexo_reportes.py)
cd "$repo"
exec 9>"$repo/.git/serumich-deploy.lock"
flock -n 9 || { echo 'Ya existe otro despliegue'; exit 1; }
sudo -n true
test -s "$respaldo/base.dump"
pg_restore --list "$respaldo/base.dump" >/dev/null
anterior=$(cat "$respaldo/commit-anterior")
[ "$(git rev-parse HEAD)" = "$anterior" ]
[ "$(git -C "$candidato" rev-parse HEAD)" = "$revision" ]
git diff --cached --quiet
git diff --binary | cmp - "$respaldo/cambios-locales.patch"
cmp backend/.env "$respaldo/backend.env"
cmp backend/app/database.py "$candidato/backend/app/database.py"
sudo -n cat /etc/serumich/serumich.env | cmp - "$respaldo/servicio.env"
sudo -n cat /etc/systemd/system/serumich.service | cmp - "$respaldo/serumich.service"
git merge-base --is-ancestor "$anterior" "$revision"
git diff --quiet "$anterior" "$revision" -- backend/requirements.txt backend/app/database.py
git diff --quiet "$anterior" -- backend/app ':!backend/app/main.py' ':!backend/app/database.py'
git -C "$candidato" diff --cached --quiet
git -C "$candidato" diff --quiet -- . ':!backend/app/main.py' ':!backend/app/database.py' ':!backend/.env'
test -z "$(git ls-files --others --exclude-standard backend/app)"
test -z "$(git -C "$candidato" ls-files --others --exclude-standard backend/app)"
git diff --binary -- backend/app/main.py | cmp - "$respaldo/ajuste-main-produccion.patch"
git apply --reverse --check "$respaldo/ajuste-main-produccion.patch"
git -C "$candidato" apply --reverse --check "$respaldo/ajuste-main-produccion.patch"
for archivo in "${archivos[@]}"; do
  tar -tzf "$respaldo/codigo-anterior.tar.gz" "$archivo" >/dev/null
done
pid=$(systemctl show serumich.service --value -p MainPID)
test "$pid" -gt 1

# Usa exactamente el entorno del servicio, sin imprimir sus credenciales.
"$python" - "$pid" "$candidato/backend" <<'PY'
import os
import sys
from ipaddress import ip_interface
from pathlib import Path
entorno = {}
for entrada in Path('/proc', sys.argv[1], 'environ').read_bytes().split(b'\0'):
    if b'=' in entrada:
        clave, valor = entrada.split(b'=', 1)
        entorno[os.fsdecode(clave)] = os.fsdecode(valor)
os.environ.clear()
os.environ.update(entorno)
os.chdir(sys.argv[2])
sys.path.insert(0, sys.argv[2])
from app.database import engine
from sqlalchemy import text
with engine.connect() as conexion:
    base, host, puerto = conexion.execute(text(
        'SELECT current_database(), inet_server_addr()::text, inet_server_port()'
    )).one()
assert base == 'facebook_clone', 'Base inesperada'
direccion = str(ip_interface(host).ip) if host else None
assert direccion in (None, '127.0.0.1', '::1', '172.16.123.109'), 'Servidor de base inesperado'
assert puerto in (None, 5432), 'Puerto de base inesperado'
from app.main import app
spec = app.openapi()
campos = {'lugar_acta', 'ine_saliente', 'domicilio_saliente', 'telefono_saliente',
          'nombramiento_saliente', 'asignacion_saliente', 'asignado_por_saliente'}
for nombre in ('ActaCreate', 'ActaUpdate', 'ActaResponse', 'ActaDocumentoResponse'):
    assert campos <= set(spec['components']['schemas'][nombre]['properties']), nombre
assert 'children' in spec['components']['schemas']['UnidadJerarquicaResponse']['properties']
assert all(os.path.isabs(os.environ[k]) for k in ('SERUMICH_UPLOAD_DIR', 'SERUMICH_STATIC_ROOT'))
assert os.environ.get('PUBLIC_API_URL', '').startswith(('https://', 'http://'))
engine.dispose()
print('Candidato importado; conexión local a facebook_clone y rutas verificadas')
PY

# Respaldo reciente, además del respaldo inicial ya verificado.
test ! -e "$respaldo/base-preactivacion.dump"
sudo -n -u postgres pg_dump -Fc --dbname=facebook_clone > "$respaldo/base-preactivacion.dump"
test -s "$respaldo/base-preactivacion.dump"
pg_restore --list "$respaldo/base-preactivacion.dump" >/dev/null
detenido=0
codigo_cambiado=0
rollback() {
  fallo=$?
  trap - ERR
  set +e
  if [ "$detenido" = 1 ]; then
    sudo -n systemctl stop serumich.service
    if [ "$codigo_cambiado" = 1 ]; then
      git reset --mixed "$anterior"
      tar -xzf "$respaldo/codigo-anterior.tar.gz" -C "$repo" "${archivos[@]}"
    fi
    sudo -n systemctl start serumich.service
    if curl -fsS --max-time 5 --retry 10 --retry-connrefused --retry-delay 1 "$api/openapi.json" >/dev/null; then
      echo 'Servicio anterior recuperado; columnas aditivas conservadas'
    else
      echo 'REVISAR SERVICIO: la recuperación no superó la comprobación HTTP'
    fi
  fi
  echo "Despliegue detenido. Respaldo: $respaldo"
  exit "$fallo"
}
trap rollback ERR
detenido=1
sudo -n systemctl stop serumich.service

# Conserva una firma de todas las columnas originales de cada acta y sus vínculos.
columnas=$(sudo -n -u postgres psql -X -At -d facebook_clone -v ON_ERROR_STOP=1 -c \
  "SELECT 'ARRAY[' || string_agg(quote_literal(column_name), ',' ORDER BY ordinal_position) || ']::text[]' FROM information_schema.columns WHERE table_schema='public' AND table_name='acta_entrega_recepcion';")
test -n "$columnas"
consulta="SELECT json_build_object(
 'usuarios', (SELECT count(*) FROM public.users),
 'actas', (SELECT count(*) FROM public.acta_entrega_recepcion),
 'anexos', (SELECT count(*) FROM public.anexos),
 'contenido_actas', (SELECT md5(COALESCE(jsonb_agg((SELECT jsonb_object_agg(e.key,e.value) FROM jsonb_each(to_jsonb(a)) e WHERE e.key=ANY($columnas)) ORDER BY a.id)::text,'[]')) FROM public.acta_entrega_recepcion a),
 'vinculos', (SELECT md5(COALESCE(jsonb_agg(jsonb_build_array(id,acta_id) ORDER BY id)::text,'[]')) FROM public.anexos));"
sudo -n -u postgres psql -X -At -d facebook_clone -v ON_ERROR_STOP=1 -c "$consulta" > "$respaldo/integridad-antes.json"
for archivo in 005_actas_participantes.sql 006_anexo_fojas.sql 007_actas_datos_funcionarios.sql; do
  sudo -n -u postgres env PGOPTIONS='-c lock_timeout=5000 -c statement_timeout=60000' \
    psql -X -d facebook_clone -v ON_ERROR_STOP=1 < "$candidato/backend/migrations/$archivo"
done
sudo -n -u postgres psql -X -At -d facebook_clone -v ON_ERROR_STOP=1 -c "$consulta" > "$respaldo/integridad-despues.json"
cmp "$respaldo/integridad-antes.json" "$respaldo/integridad-despues.json"
echo 'Migraciones verificadas: actas, conteos y vínculos conservados'

codigo_cambiado=1
git apply --reverse "$respaldo/ajuste-main-produccion.patch"
git -c core.hooksPath=/dev/null merge --ff-only "$revision"
cp "$candidato/backend/app/main.py" backend/app/main.py
cmp backend/app/database.py "$candidato/backend/app/database.py"
cmp backend/.env "$respaldo/backend.env"
for archivo in "${archivos[@]}"; do
  cmp "$archivo" "$candidato/$archivo"
done
sudo -n systemctl start serumich.service
curl -fsS --max-time 5 --retry 20 --retry-connrefused --retry-delay 1 \
  "$api/openapi.json" > "$respaldo/openapi-activo.json"
"$python" - "$respaldo/openapi-activo.json" <<'PY'
import json
import sys
spec = json.load(open(sys.argv[1]))
campos = {'lugar_acta', 'ine_saliente', 'domicilio_saliente', 'telefono_saliente',
          'nombramiento_saliente', 'asignacion_saliente', 'asignado_por_saliente'}
for nombre in ('ActaCreate', 'ActaUpdate', 'ActaResponse', 'ActaDocumentoResponse'):
    assert campos <= set(spec['components']['schemas'][nombre]['properties']), nombre
assert 'children' in spec['components']['schemas']['UnidadJerarquicaResponse']['properties']
respuesta = spec['paths']['/anexos']['get']['responses']['200']['content']['application/json']['schema']
nombre = respuesta['items']['$ref'].rsplit('/', 1)[-1]
assert 'fojas_por_defecto' in spec['components']['schemas'][nombre]['properties']
for ruta, metodo in [('/actas/{acta_id}', 'put'), ('/anexos/{anexo_id}/reporte', 'post'), ('/pdf', 'post')]:
    assert spec['paths'][ruta][metodo].get('security'), ruta
print('Esquemas y autenticación de producción verificados')
PY
curl -fsS --max-time 15 "$api/anexos?limit=1" | "$python" -c \
  'import json,sys; datos=json.load(sys.stdin); assert isinstance(datos,list); assert not datos or "fojas_por_defecto" in datos[0]; print("Consulta de anexos verificada")'
sudo -n systemctl is-active --quiet serumich.service
printf '%s\n' "$revision" > "$respaldo/commit-desplegado"
trap - ERR
echo "PRODUCCION ACTIVA: $revision"
echo "Respaldo y registro: $respaldo"
