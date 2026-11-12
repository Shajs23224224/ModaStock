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
Configura DATABASE_URL en .env. No subas secretos.

## Migraciones y ejecución
```bash
alembic revision --autogenerate -m "initial schema"
alembic upgrade head
uvicorn app.main:app --reload
pytest
```
Revisa el SQL autogenerado y pruébalo en PostgreSQL antes de aplicar en entornos persistentes. No hay migración aplicada todavía. OpenAPI: /docs.

El servicio de movimientos usa SELECT FOR UPDATE, transacción e idempotencia. Su endpoint HTTP permanece en 501 hasta la Fase 5 para no confiar en un user_id proporcionado por el cliente. Los endpoints de catálogo son de desarrollo y no deben exponerse públicamente sin autenticación/autorización. SQLite solo sirve para pruebas rápidas y no valida concurrencia PostgreSQL.
