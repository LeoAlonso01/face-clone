from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Obtener IP real (X-Forwarded-For) o fallback a cliente
        xff = request.headers.get('x-forwarded-for')
        if xff:
            client_ip = xff.split(',')[0].strip()
        else:
            client = request.client
            client_ip = client.host if client else None

        # Guardar en request.state para usarlo en endpoints
        request.state.client_ip = client_ip
        request.state.user_agent = request.headers.get('user-agent')

        response = await call_next(request)
        return response
