# Documentación de la API - Sistema SERUMICHV2BE

## 📋 Descripción General

Sistema backend desarrollado con FastAPI para la gestión de unidades responsables, actas de entrega-recepción y anexos documentales.

## 🚀 Características Principales

- **Autenticación JWT** con roles de usuario
- **Gestión de Unidades Responsables** con estructura jerárquica
- **Actas de Entrega-Recepción** con anexos documentales
- **API RESTful** con documentación automática (Swagger/ReDoc)
- **Base de datos PostgreSQL** con SQLAlchemy ORM

## 📊 Estructura del Proyecto

```
backend/
├── app/
│   ├── main.py              # Endpoints principales de la API
│   ├── models.py            # Modelos de base de datos
│   ├── schemas.py           # Esquemas Pydantic para validación
│   ├── auth.py              # Autenticación y seguridad
│   ├── database.py          # Configuración de base de datos
│   └── acta_entrega_routes.py # Rutas de actas (pendiente)
├── alembic/                 # Migraciones de base de datos
├── static/                  # Archivos estáticos
├── uploads/                 # Archivos subidos
└── docs/                    # Documentación (esta carpeta)
```

## 🔗 Enlaces Rápidos

- [Autenticación y Usuarios](./autenticacion.md)
- [Unidades Responsables](./unidades-responsables.md)
- [Actas de Entrega-Recepción](./actas.md)
- [Anexos Documentales](./anexos.md)
- [Modelos de Datos](./modelos.md)
- [Esquemas Pydantic](./esquemas.md)

## 🛠️ Configuración y Uso

### Requisitos
- Python 3.8+
- PostgreSQL
- Docker (opcional)

### Instalación

```bash
# Clonar el repositorio
cd face-clone/backend

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de PostgreSQL

# Ejecutar la aplicación
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Variables de Entorno

```env
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_password
POSTGRES_DB=nombre_base_datos
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
SECRET_KEY=tu_clave_secreta_jwt
```

## 📚 Documentación Interactiva

Una vez ejecutada la aplicación, accede a:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Endpoint raíz**: http://localhost:8000/

## 🔐 Roles de Usuario

- **USER**: Usuario básico con permisos limitados
- **ADMIN**: Administrador con acceso completo
- **AUDITOR**: Usuario con permisos de solo lectura

## 📞 Soporte

Para reportar issues o solicitar características, contactar al equipo de desarrollo.

## 🏢 Contexto Institucional

SERUMICH V2.0 es un sistema en producción utilizado por la Universidad Michoacana de San Nicolás de Hidalgo para la gestión de procesos de entrega-recepción entre dependencias.

El sistema permite registrar y auditar información crítica, garantizando trazabilidad, transparencia y control administrativo.

---

## 🏗️ Arquitectura del Sistema

El sistema sigue una arquitectura basada en API REST:

- **Frontend**: Next.js + TypeScript
- **Backend**: FastAPI
- **Base de Datos**: PostgreSQL
- **Infraestructura**: Docker

### Flujo general:

Usuario → Frontend → API FastAPI → PostgreSQL

---

## 🔄 Flujo Principal

1. Usuario inicia sesión
2. Gestiona su unidad responsable
3. Crea actas de entrega-recepción
4. Adjunta anexos
5. Sistema registra auditoría automáticamente

---

## 📌 Estado del Proyecto

- ✅ Sistema en producción
- ✅ Usuarios reales activos
- 🔄 En mejora continua

---

## 🧠 Mantenimiento y Continuidad

Este sistema está diseñado para ser mantenido por futuros desarrolladores.  
Se recomienda:

- Revisar documentación en `/docs`
- Usar migraciones con Alembic
- Mantener control de versiones

## Diagrama

┌──────────────────────┐
│      USUARIO         │
└─────────┬────────────┘
          │
          ▼
┌──────────────────────┐
│   FRONTEND (Next.js) │
│   TypeScript         │
└─────────┬────────────┘
          │ API REST
          ▼
┌──────────────────────┐
│   BACKEND (FastAPI)  │
│   Autenticación JWT  │
│   Lógica de negocio  │
└─────────┬────────────┘
          │ ORM (SQLAlchemy)
          ▼
┌──────────────────────┐
│   PostgreSQL DB      │
│   Actas / Anexos     │
│   Usuarios / Logs    │
└──────────────────────┘

## Flujo de operacion

Login → Token JWT → Crear Acta → Agregar Anexos → Guardar → Auditoría

---
*Última actualización: Marzo 2026*