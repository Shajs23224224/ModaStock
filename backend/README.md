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

Configura `DATABASE_URL`, `CORS_ORIGINS` y reemplaza `JWT_SECRET_KEY` por un secreto aleatorio de al menos 32 caracteres. `APP_ENV` admite `development`, `test` o `production`. El secreto de ejemplo solo se admite en desarrollo/pruebas. No subas secretos.

## Base de datos y roles
```bash
alembic upgrade head
python -m app.seed_roles
```
Revisa las migraciones y ejecútalas primero en una base de pruebas.

El registro público asigna únicamente STAFF. Para habilitar el primer administrador, realiza una asignación administrativa controlada directamente en PostgreSQL; nunca expongas ese procedimiento como endpoint público.

## Cuenta y catálogo de demostración
El arranque del contenedor ejecuta `app.seed_demo` después de las migraciones y del seed de roles. Para habilitarlo, configura estas variables en el entorno del servicio:
- `DEMO_ACCOUNT_EMAIL`: por defecto `demo@modastock.app`.
- `DEMO_ACCOUNT_NAME`: por defecto `Cuenta de demostración`.
- `DEMO_ACCOUNT_PASSWORD`: obligatorio, mínimo 12 caracteres; guárdalo como variable secreta y no lo incluyas en el repositorio.

El proceso es idempotente: crea o habilita únicamente la cuenta indicada, le asigna el rol MANAGER y carga cuatro productos de ropa, cinco variantes y existencias iniciales con movimientos de entrada trazables. Si `DEMO_ACCOUNT_PASSWORD` no está configurada, omite la carga demo. El registro público continúa asignando STAFF.

## Ejecución y pruebas
```bash
uvicorn app.main:app --reload
pytest
```
OpenAPI: /docs.

## Comprobaciones operativas
- `GET /health`: liveness del proceso de API.
- `GET /health/ready`: readiness; ejecuta `SELECT 1` y devuelve HTTP 503 si la base de datos no está disponible.

## Autenticación y permisos
- Registro público: STAFF únicamente.
- Lectura de catálogo, variantes, existencias e historial: cualquier usuario autenticado.
- Crear productos y variantes, y configurar stock mínimo: ADMIN o MANAGER.
- Registrar movimientos: STAFF, MANAGER o ADMIN; la identidad se toma del JWT.

## API de inventario
- `GET /api/v1/sizes`, `GET /api/v1/colors`: catálogos activos.
- `GET /api/v1/variants?q=...`: búsqueda por SKU, producto, talla o color; incluye saldo.
- `GET /api/v1/inventory/stock?low_stock_only=true`: consulta de existencias y alertas por umbral.
- `GET /api/v1/variants/{id}/stock`: saldo de una variante.
- `PATCH /api/v1/variants/{id}/minimum-stock`: configura el umbral mínimo.
- `GET /api/v1/inventory/movements`: historial de movimientos, filtrable por variante o tipo.
- `POST /api/v1/products/{id}/variants`: crea variante y saldo inicial en una transacción.
- `POST /api/v1/inventory/movements`: registra entradas, salidas o ajustes.

Cada movimiento debe incluir una cabecera `Idempotency-Key` única. Reutilizar la clave con datos distintos devuelve HTTP 409. Las salidas y ajustes de disminución que dejen saldo negativo se rechazan. Los movimientos se consultan como historial append-only.

## Seguridad y límites
Contraseñas: Argon2. Tokens: JWT HS256, duración configurable mediante `ACCESS_TOKEN_EXPIRE_MINUTES`. Antes de producción se requiere HTTPS, gestión y rotación de secretos, limitación de intentos de login y política de respaldo.

SQLite solo sirve para pruebas rápidas y no valida bloqueos ni concurrencia PostgreSQL. La serialización con SELECT FOR UPDATE debe validarse con PostgreSQL de pruebas. No se implementan refresh tokens ni revocación inmediata en este MVP.
