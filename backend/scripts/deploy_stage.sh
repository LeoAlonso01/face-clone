#!/usr/bin/env bash
# Exclusivo de stage: conserva producción y las configuraciones locales.
set -Eeuo pipefail
umask 077
[ "$(hostname -s)" = investigacion ] || { echo "Servidor incorrecto"; exit 1; }
repo="$HOME/serumich-stage-backend"
config="$HOME/.config/serumich-stage/backend.env"
respaldo=$(realpath -e -- "${1:?Indica el respaldo verificado}")
revision="${2:?Indica el SHA completo}"
[[ "$revision" =~ ^[0-9a-f]{40}$ ]] || exit 1
case "$respaldo" in "$HOME"/serumich-stage-pre007.*) ;; *) echo "Respaldo inesperado"; exit 1 ;; esac
cd "$repo"
sudo -v
test -s "$respaldo/base-stage.dump"
pg_restore --list "$respaldo/base-stage.dump" >/dev/null
test -f "$config"
python3 - "$config" <<'PY'
import sys
config = dict(line.strip().split('=', 1) for line in open(sys.argv[1]) if '=' in line and not line.lstrip().startswith('#'))
assert config.get('POSTGRES_DB') == 'serumich_stage', 'Base de configuración inesperada'
assert config.get('POSTGRES_HOST') in ('127.0.0.1', 'localhost'), 'Host de base inesperado'
assert config.get('POSTGRES_PORT') == '5432', 'Puerto de base inesperado'
print('Archivo de conexión de stage verificado')
PY
cmp backend/app/database.py "$respaldo/database.py"
git cat-file -e "$revision^{commit}"
git merge-base --is-ancestor HEAD "$revision"
sudo docker exec serumich-stage-api python -c 'from app.database import engine; assert engine.url.database == "serumich_stage" and engine.url.host in ("127.0.0.1", "localhost"), "Conexión inesperada"; print("Conexión activa de stage verificada")'
cp "$config" "$respaldo/backend.env"
candidato="$respaldo/candidato"
contexto="$respaldo/contexto"
test ! -e "$candidato"
test ! -e "$contexto"
git worktree add --detach "$candidato" "$revision"
cp "$respaldo/database.py" "$candidato/backend/app/database.py"
mkdir "$contexto"
cp "$candidato/backend/requirements.txt" "$contexto/requirements.txt"
cp -a "$candidato/backend/app" "$contexto/app"
cat > "$contexto/Dockerfile" <<'DOCKERFILE'
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"]
DOCKERFILE
imagen="serumich-stage-api:${revision:0:12}"
sudo docker build --label "serumich.stage.revision=$revision" -t "$imagen" "$contexto"
conteos="SELECT json_build_object('usuarios',(SELECT count(*) FROM public.users),'actas',(SELECT count(*) FROM public.acta_entrega_recepcion),'anexos',(SELECT count(*) FROM public.anexos),'vinculados',(SELECT count(*) FROM public.anexos WHERE acta_id IS NOT NULL AND acta_id <> 0));"
sudo -u postgres psql -X -At -d serumich_stage -v ON_ERROR_STOP=1 -c "$conteos" > "$respaldo/conteos-antes.json"
for archivo in 005_actas_participantes.sql 006_anexo_fojas.sql 007_actas_datos_funcionarios.sql; do
  sudo -u postgres env PGOPTIONS='-c lock_timeout=5000 -c statement_timeout=60000' psql -X -d serumich_stage -v ON_ERROR_STOP=1 < "$candidato/backend/migrations/$archivo"
done
sudo -u postgres psql -X -At -d serumich_stage -v ON_ERROR_STOP=1 -c "$conteos" > "$respaldo/conteos-despues.json"
cmp "$respaldo/conteos-antes.json" "$respaldo/conteos-despues.json"
echo "Migraciones aplicadas; conteos y vínculos conservados"
probe="serumich-stage-probe-${revision:0:12}"
anterior="serumich-stage-api-prev-${revision:0:12}"
if sudo docker inspect "$probe" >/dev/null 2>&1; then
  echo "Ya existe el contenedor de prueba; revisar antes de continuar"; exit 1
fi
if sudo docker inspect "$anterior" >/dev/null 2>&1; then
  echo "Ya existe un contenedor anterior con ese nombre; revisar antes de continuar"; exit 1
fi
renombrado=0
detenido=0
nuevo_intentado=0
rollback() {
  fallo=$?
  trap - ERR
  set +e
  sudo docker rm -f "$probe" >/dev/null 2>&1
  if [ "$renombrado" = 1 ]; then
    if [ "$nuevo_intentado" = 1 ] && sudo docker inspect serumich-stage-api >/dev/null 2>&1; then
      etiqueta=$(sudo docker inspect serumich-stage-api --format '{{index .Config.Labels "serumich.stage.revision"}}')
      if [ "$etiqueta" != "$revision" ]; then
        echo "Contenedor inesperado; revisar manualmente. No se eliminará."
        exit "$fallo"
      fi
      sudo docker rm -f serumich-stage-api
    fi
    sudo docker rename "$anterior" serumich-stage-api
    sudo docker start serumich-stage-api
    echo "Se intentó restaurar el contenedor anterior; las columnas aditivas se conservan."
  elif [ "$detenido" = 1 ]; then
    sudo docker start serumich-stage-api
  fi
  echo "Despliegue detenido. Respaldo: $respaldo"
  exit "$fallo"
}
trap rollback ERR
iniciar() {
  nombre="$1"
  puerto="$2"
  politica="$3"
  sudo docker run -d --name "$nombre" --restart "$politica" --network host \
    --label "serumich.stage.revision=$revision" --env-file "$config" -e APP_ENV=stage \
    -v "$candidato/backend/app:/app/app:ro" \
    -v "$HOME/.local/share/serumich-stage/static:/app/static" \
    -v "$HOME/.local/share/serumich-stage/uploads:/app/uploads" \
    "$imagen" python -m uvicorn app.main:app --host 127.0.0.1 --port "$puerto"
}
verificar() {
  puerto="$1"
  salida="$2"
  curl -fsS --max-time 5 --retry 15 --retry-connrefused --retry-delay 1 \
    "http://127.0.0.1:$puerto/openapi.json" > "$salida"
  python3 - "$salida" <<'PY'
import json, sys
spec = json.load(open(sys.argv[1]))
for nombre in ('ActaCreate', 'ActaUpdate', 'ActaResponse', 'ActaDocumentoResponse'):
    campos = spec['components']['schemas'][nombre]['properties']
    assert {'lugar_acta', 'ine_saliente', 'domicilio_saliente', 'telefono_saliente', 'nombramiento_saliente', 'asignacion_saliente', 'asignado_por_saliente'} <= set(campos), nombre
assert 'children' in spec['components']['schemas']['UnidadJerarquicaResponse']['properties']
assert 'fojas_por_defecto' in spec['components']['schemas']['AnexoResponse']['properties']
for ruta, metodo in [('/actas/{acta_id}', 'put'), ('/anexos/{anexo_id}/reporte', 'post'), ('/pdf', 'post')]:
    assert spec['paths'][ruta][metodo].get('security'), ruta
print('Esquemas y autenticación verificados')
PY
  curl -fsS --max-time 10 "http://127.0.0.1:$puerto/anexos?limit=1" | \
    python3 -c 'import json,sys; datos=json.load(sys.stdin); assert isinstance(datos,list); assert not datos or "fojas_por_defecto" in datos[0]; print("Consulta de anexos verificada")'
}
iniciar "$probe" 18082 no
verificar 18082 "$respaldo/openapi-candidato.json"
sudo docker stop "$probe" >/dev/null
sudo docker rm "$probe" >/dev/null
sudo docker stop serumich-stage-api >/dev/null
detenido=1
sudo docker rename serumich-stage-api "$anterior"
renombrado=1
nuevo_intentado=1
iniciar serumich-stage-api 8000 unless-stopped
verificar 8000 "$respaldo/openapi-activo.json"
printf '%s\n' "$revision" > "$respaldo/commit-desplegado"
printf '%s\n' "$respaldo" > "$HOME/.config/serumich-stage/ultimo-despliegue"
trap - ERR
echo "STAGE ACTIVO: $revision"
echo "Contenedor anterior conservado: $anterior"
echo "Código activo: $candidato"
echo "Respaldo: $respaldo"
