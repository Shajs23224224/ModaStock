# Fase 4 — Backend y servicios API
Estado: primera implementación; pendiente validación en PostgreSQL.

## Implementación
El directorio backend contiene configuración, sesión SQLAlchemy, once modelos ORM alineados con Fase 3, esquemas Pydantic, endpoints de catálogo, servicio transaccional de inventario, configuración Alembic y pruebas.

## Endpoints
- GET /health
- POST /api/v1/products
- GET /api/v1/products (limit/offset)
- GET /api/v1/products/{id}
- POST /api/v1/products/{id}/variants (crea saldo cero en la misma transacción)
- GET /api/v1/variants/{id}/stock
- POST /api/v1/inventory/movements: HTTP 501 temporal hasta autenticación/autorización de Fase 5.

## Consistencia
El servicio calcula stock en servidor, bloquea filas con SELECT FOR UPDATE, actualiza saldo e historial atómicamente y admite clave idempotente. El cliente no puede elegir el usuario que firma el movimiento. Las variantes y saldos iniciales se crean de forma atómica.

## Pendientes
Generar y revisar migración inicial con Alembic en PostgreSQL; ejecutar pruebas; verificar concurrencia, rollback e idempotencia en PostgreSQL; completar seguridad en Fase 5. SQLite no demuestra garantías de bloqueo PostgreSQL.
