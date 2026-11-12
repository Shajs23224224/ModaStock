# Backend ModaStock
FastAPI + SQLAlchemy 2 + Pydantic + Alembic.

## Instalación
Python 3.11+ y PostgreSQL 15+. Desde esta carpeta:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
cp .env.example .env
```
Configura DATABASE_URL y reemplaza JWT_SECRET_KEY por un secreto aleatorio de al menos 32 caracteres. No subas secretos.

## Base de datos y roles
```bash
alembic upgrade head
python -m app.seed_roles
```
Revisa las migraciones y ejecútalas primero en una base de pruebas. No hay migración aplicada ni base desplegada por este repositorio.

El registro público asigna únicamente STAFF. Para habilitar el primer administrador, realiza una asignación administrativa controlada directamente en PostgreSQL, después de inicializar los roles:
```sql
UPDATE users
SET role_id = (SELECT id FROM roles WHERE name = 'ADMIN')
WHERE email = lower('correo-administrador@ejemplo.com');
```
Sustituye el correo por el de la cuenta autorizada. No expongas este procedimiento como endpoint público.

## Ejecución y pruebas
```bash
uvicorn app.main:app --reload
pytest
```
OpenAPI: /docs.

## Autenticación
- `POST /api/v1/auth/register`: alta pública, rol STAFF.
- `POST /api/v1/auth/login`: recibe email y password; devuelve JWT.
- `GET /api/v1/auth/me`: perfil del usuario autenticado.
- Enviar `Authorization: Bearer <token>` para rutas protegidas.
- `POST /api/v1/inventory/movements`: requiere STAFF, MANAGER o ADMIN; la identidad se toma del token.
- Lectura de catálogo y stock: cualquier usuario autenticado.
- Crear productos y variantes: ADMIN o MANAGER.

Contraseñas: Argon2. Tokens: JWT HS256, duración configurable mediante ACCESS_TOKEN_EXPIRE_MINUTES. El secreto de ejemplo es solo para desarrollo. Antes de producción se requiere HTTPS, gestión y rotación de secretos, limitación de intentos de login, política de respaldo y revisión de permisos.

SQLite solo sirve para pruebas rápidas y no valida bloqueos ni concurrencia PostgreSQL. No se implementan refresh tokens ni revocación inmediata en este MVP.
