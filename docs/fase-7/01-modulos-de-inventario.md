# Fase 7 — Módulos de inventario

## Objetivo
Completar la gestión operativa de inventario de ModaStock: variantes de prendas, existencias, umbrales de reposición y trazabilidad de movimientos.

## Modelo y reglas
- Un producto representa el modelo o referencia comercial; una variante representa la combinación única producto + talla + color.
- Cada variante tiene SKU único y una fila de saldo asociada, creada en la misma transacción que la variante.
- Las existencias se consultan por SKU, producto, talla, color o identificador de variante.
- El saldo no puede ser negativo. Las entradas, salidas y ajustes actualizan saldo y registran el movimiento en una misma transacción.
- Los movimientos son un historial de solo anexado desde la API: no se ofrecen operaciones de edición o borrado.
- La clave Idempotency-Key evita duplicar una operación; reutilizarla con datos distintos produce HTTP 409.
- El umbral mínimo se puede configurar por variante; se considera bajo stock cuando quantity <= minimum_quantity.
- Las operaciones de escritura de catálogo y configuración de umbrales requieren ADMIN o MANAGER. Consulta e historial requieren autenticación.

## Endpoints
| Método | Ruta | Uso |
|---|---|---|
| GET | /api/v1/sizes | Consultar tallas activas |
| GET | /api/v1/colors | Consultar colores activos |
| GET | /api/v1/variants | Buscar variantes por SKU, producto, talla o color |
| GET | /api/v1/inventory/stock | Consultar saldos; admite low_stock_only y q |
| GET | /api/v1/variants/{id}/stock | Consultar saldo de una variante |
| PATCH | /api/v1/variants/{id}/minimum-stock | Configurar umbral mínimo |
| GET | /api/v1/inventory/movements | Consultar historial, opcionalmente por variante o tipo |
| POST | /api/v1/products/{id}/variants | Crear variante y saldo inicial en cero |
| POST | /api/v1/inventory/movements | Registrar IN, OUT o ADJUSTMENT |

## Registro de movimientos
Enviar Authorization: Bearer <token>. Para prevenir reintentos duplicados, incluir una cabecera Idempotency-Key única por operación. La salida no permite que el saldo quede negativo. Para ajustes se exige adjustment_direction INCREASE o DECREASE.

## Consideraciones técnicas
- SQLAlchemy usa SELECT FOR UPDATE sobre la variante y su saldo para serializar operaciones concurrentes en PostgreSQL.
- La restricción CHECK quantity >= 0 y la unicidad de la clave idempotente complementan las validaciones de aplicación.
- SQLite no reproduce los bloqueos de fila de PostgreSQL; la concurrencia real debe verificarse en una instancia PostgreSQL de pruebas.
- No se ejecutaron migraciones ni se modificó una base de datos remota en esta fase.
- El historial se expone en lectura; las correcciones deben registrarse como movimientos compensatorios.
