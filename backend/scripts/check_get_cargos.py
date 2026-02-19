import httpx, json, sys
url = 'http://localhost:8000/cargos'
try:
    r = httpx.get(url, timeout=10.0)
    out = {'status_code': r.status_code, 'text': r.text}
except Exception as e:
    out = {'error': str(e)}
with open('check_get_cargos_output.json', 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print('wrote check_get_cargos_output.json')
