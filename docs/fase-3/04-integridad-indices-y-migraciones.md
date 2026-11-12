# Integridad, índices y estrategia de migraciones — ModaStock

- **Fase:** 3 — Diseño de base de datos
- **Versión:** 1.0
- **Estado:** estrategia de diseño; no hay migraciones aplicadas a una base real.

## 1. Integridad referencial

Se aplican claves primarias UUID y claves foráneas para impedir registros huérfanos. Las relaciones históricas usan `ON DELETE RESTRICT` para que no se pueda borrar una variante, usuario o proveedor que esté referenciado por movimientos. Para el usuario de un evento de auditoría se permite `SET NULL`, conservando el evento.

Las entidades de catálogo se desactivan mediante `is_active` en lugar de eliminarse físicamente cuando tienen historial asociado.

## 2. Restricciones de negocio

| Regla | Protección prevista |
|---|---|
| Email no repetido ignorando mayúsculas | Restricción única sobre `lower(email)` |
| Referencia de producto única | UNIQUE en `model_reference` |
| SKU único | UNIQUE en `product_variants.sku` |
| Código de barras único si existe | UNIQUE nullable en `barcode` |
| Una variante por producto-talla-color | UNIQUE compuesto |
| Un saldo por variante | UNIQUE en `inventory_balances.variant_id` |
| Cantidad y stock no negativos | CHECK en columnas |
| Tipo de movimiento permitido | CHECK |
| Dirección de ajuste coherente | CHECK condicional |
| Saldo anterior y posterior matemáticamente coherentes | CHECK por tipo de movimiento |
| Reintentos sin duplicar movimientos | Índice único parcial de `idempotency_key` |

La base de datos no puede garantizar con un CHECK ordinario que el saldo de una tabla coincida con el último movimiento de otra. Esa consistencia se garantiza mediante transacción, bloqueo de fila y pruebas de integración.

## 3. Concurrencia y transacción de inventario

Para registrar un movimiento:

1. Abrir una transacción.
2. Buscar el saldo por variante usando `SELECT ... FOR UPDATE`.
3. Validar existencia de la variante, estado, permiso, tipo y cantidad.
4. Calcular el saldo resultante en backend.
5. Rechazar la operación si el resultado es negativo.
6. Actualizar `inventory_balances`.
7. Insertar `inventory_movements` con saldos anterior y posterior, usuario, motivo y clave de idempotencia.
8. Confirmar la transacción.

Si ocurre un error, se revierte el cambio de saldo y el movimiento. Para dos salidas simultáneas sobre la misma variante, el bloqueo serializa la modificación y evita vender unidades inexistentes. Las solicitudes con la misma clave de idempotencia deben devolver el resultado previamente creado o un conflicto controlado, nunca duplicar el movimiento.

La aplicación debe establecer un orden consistente al bloquear varias variantes en una operación futura para reducir deadlocks.

## 4. Inmutabilidad y auditoría

- La cuenta de aplicación no debe tener permiso ordinario para borrar movimientos.
- No se permite editar un movimiento confirmado.
- Los errores se corrigen mediante un movimiento compensatorio con motivo y referencia al movimiento original.
- Las acciones administrativas sensibles generan eventos de auditoría.
- No registrar contraseñas, tokens, secretos ni datos sensibles en JSONB.
- Las tareas de mantenimiento deben usar credenciales separadas y dejar registro.

## 5. Índices

Los índices se eligen según consultas previstas:

- Índices de claves foráneas usadas en joins.
- Índice compuesto `(variant_id, created_at DESC)` para historial de una variante.
- Índices por usuario y fecha para auditoría operativa.
- Índice por proveedor y fecha para entradas.
- Índice por fecha para reportes temporales.
- Índice parcial de idempotencia para claves no nulas.

Las restricciones UNIQUE ya crean índices en PostgreSQL. No se deben duplicar índices equivalentes. Los índices adicionales deben revisarse con `EXPLAIN (ANALYZE, BUFFERS)` cuando existan datos representativos.

## 6. Estrategia de migraciones Alembic

1. Configurar SQLAlchemy con modelos alineados con este diseño.
2. Crear migración inicial versionada con Alembic.
3. Revisar manualmente el SQL generado; no confiar ciegamente en autogenerate.
4. Aplicar migración en base de desarrollo limpia.
5. Ejecutar pruebas de restricciones, relaciones y rollback.
6. Probar upgrade desde la revisión anterior y downgrade cuando sea seguro.
7. Ejecutar migraciones en CI contra PostgreSQL.
8. Respaldar la base antes de migraciones de producción.
9. No editar una migración ya aplicada; crear una nueva revisión correctiva.

Los datos iniciales de roles, si se incorporan, deben cargarse mediante una operación reproducible e idempotente, sin contraseñas predeterminadas inseguras.

## 7. Estrategia de respaldo y reconciliación

- Definir periodicidad, retención y responsables antes de producción.
- Proteger respaldos con cifrado y acceso limitado.
- Probar restauración, no solo creación de copias.
- Programar una reconciliación que compare el saldo de cada variante con el saldo reconstruido desde el historial, considerando el saldo inicial registrado.
- Registrar diferencias y resolverlas mediante ajuste autorizado, nunca mediante edición silenciosa del historial.

## 8. Pruebas de base de datos previstas

- Rechazar variantes duplicadas por producto, talla y color.
- Rechazar SKU y correos duplicados según las reglas de unicidad.
- Rechazar cantidades y saldos negativos.
- Rechazar movimientos con tipo o dirección inválidos.
- Rechazar salida que exceda existencias.
- Confirmar rollback cuando falla la inserción del movimiento después de intentar actualizar saldo.
- Simular dos salidas concurrentes y verificar que no se produzca saldo negativo.
- Verificar idempotencia ante reintentos.
- Verificar restricciones de borrado de registros históricos.
- Verificar que los reportes coincidan con saldos y movimientos.

Estas son pruebas planificadas; no se han ejecutado porque todavía no existe una implementación ni una base de datos configurada.

## 9. Condiciones de salida de la Fase 3

- [x] Entidades y relaciones identificadas.
- [x] Diagrama entidad-relación documentado.
- [x] Diccionario de datos elaborado.
- [x] Esquema SQL inicial propuesto.
- [x] Restricciones, índices y transacciones descritos.
- [x] Estrategia de migraciones y pruebas definida.
- [ ] Validar supuestos con el responsable del proyecto o comercio representativo.
- [ ] Implementar y ejecutar migración inicial en Fase 4/8.
- [ ] Verificar restricciones y concurrencia en Fase 9.

## 10. Conclusión

El diseño separa catálogo, variantes, saldo y movimientos, mantiene integridad referencial y define una estrategia transaccional para impedir inconsistencias. El SQL es una propuesta revisable que deberá convertirse en migraciones Alembic y probarse contra PostgreSQL antes de considerarse lista para producción.
