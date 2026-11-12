# Modelo lógico y diccionario de datos — ModaStock

- **Versión:** 1.0
- **Motor objetivo:** PostgreSQL
- **Convenciones:** nombres en snake_case; claves primarias UUID; fechas con zona horaria; cantidades en unidades enteras.

## 1. Convenciones de datos

- Identificadores internos: UUID.
- Fechas y horas: `timestamptz`, almacenadas en UTC.
- Cantidades de prendas: enteros, nunca fracciones en el MVP.
- Dinero: fuera del núcleo de inventario del MVP; si se incorpora, usar `numeric`, no `float`.
- Texto: `varchar` con límites donde haya una regla clara; `text` para descripciones.
- Estados: booleanos para activación y valores restringidos mediante `CHECK` para tipos de movimiento.
- Campos sensibles: almacenar hash de contraseña, nunca la contraseña original.

## 2. Diccionario de datos

### roles

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| name | varchar(50) | No | Único; nombre del rol |
| description | text | Sí | Descripción del alcance |

### users

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| role_id | UUID | No | FK a roles |
| email | varchar(254) | No | Único tras normalización |
| password_hash | varchar(255) | No | Hash Argon2id o equivalente |
| full_name | varchar(150) | No | Nombre visible |
| is_active | boolean | No | Por defecto true |
| created_at | timestamptz | No | Alta UTC |
| updated_at | timestamptz | No | Última actualización UTC |

### categories

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| name | varchar(100) | No | Nombre único |
| description | text | Sí | Descripción opcional |
| is_active | boolean | No | Por defecto true |
| created_at | timestamptz | No | Alta UTC |

### products

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| category_id | UUID | Sí | FK a categories |
| name | varchar(150) | No | Nombre comercial |
| model_reference | varchar(80) | No | Referencia única |
| description | text | Sí | Descripción opcional |
| is_active | boolean | No | Por defecto true |
| created_at | timestamptz | No | Alta UTC |
| updated_at | timestamptz | No | Última actualización UTC |

### sizes y colors

| Tabla | Campo | Tipo | Nulo | Regla / descripción |
|---|---|---|---:|---|
| sizes | id | UUID | No | PK |
| sizes | name | varchar(30) | No | Único; p. ej. XS, S, M, L, 38 |
| sizes | sort_order | integer | No | Orden de presentación |
| sizes | is_active | boolean | No | Por defecto true |
| colors | id | UUID | No | PK |
| colors | name | varchar(60) | No | Único tras normalización |
| colors | hex_code | varchar(7) | Sí | Código #RRGGBB opcional |
| colors | is_active | boolean | No | Por defecto true |

### product_variants

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| product_id | UUID | No | FK a products |
| size_id | UUID | No | FK a sizes |
| color_id | UUID | No | FK a colors |
| sku | varchar(100) | No | Único; código de variante |
| barcode | varchar(64) | Sí | Código de barras opcional, único si existe |
| is_active | boolean | No | Por defecto true |
| created_at | timestamptz | No | Alta UTC |

### inventory_balances

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| variant_id | UUID | No | FK única a product_variants |
| quantity | integer | No | Saldo actual; CHECK >= 0 |
| minimum_quantity | integer | No | Stock mínimo; CHECK >= 0; por defecto 0 |
| updated_at | timestamptz | No | Fecha de último cambio |

### suppliers

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| name | varchar(150) | No | Nombre comercial |
| contact_name | varchar(150) | Sí | Contacto opcional |
| email | varchar(254) | Sí | Correo opcional |
| phone | varchar(40) | Sí | Teléfono opcional |
| is_active | boolean | No | Por defecto true |
| created_at | timestamptz | No | Alta UTC |

### inventory_movements

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| variant_id | UUID | No | FK a product_variants |
| user_id | UUID | No | FK a users |
| supplier_id | UUID | Sí | FK a suppliers; normalmente para entradas |
| movement_type | varchar(12) | No | IN, OUT o ADJUSTMENT |
| adjustment_direction | varchar(8) | Sí | INCREASE o DECREASE solo en ajustes |
| quantity | integer | No | Cantidad positiva |
| stock_before | integer | No | Saldo previo, CHECK >= 0 |
| stock_after | integer | No | Saldo posterior, CHECK >= 0 |
| reason | varchar(250) | No | Motivo obligatorio |
| reference | varchar(100) | Sí | Documento o referencia externa |
| idempotency_key | varchar(100) | Sí | Evita duplicar una solicitud reintentada |
| created_at | timestamptz | No | Momento UTC |

### audit_events

| Campo | Tipo lógico | Nulo | Regla / descripción |
|---|---|---:|---|
| id | UUID | No | PK |
| user_id | UUID | Sí | FK a users; puede ser nulo para eventos del sistema |
| action | varchar(80) | No | Acción realizada |
| entity_type | varchar(80) | No | Tipo de entidad afectada |
| entity_id | UUID | Sí | Identificador afectado |
| details | jsonb | No | Metadatos no sensibles |
| created_at | timestamptz | No | Momento UTC |

## 3. Normalización

El modelo busca cumplir, en las tablas operativas principales, las formas normales habituales:

- **Primera forma normal:** cada columna contiene un valor atómico; tallas y colores no se guardan como listas dentro del producto.
- **Segunda forma normal:** las entidades tienen claves primarias simples; los atributos de variante dependen de la variante identificada.
- **Tercera forma normal:** los datos de categoría, talla, color, rol y proveedor se almacenan en sus entidades propias y se referencian mediante claves foráneas.

El saldo actual es una proyección operativa mantenida junto con el libro de movimientos para acelerar lecturas. Esta desnormalización controlada exige transacción atómica, auditoría y reconciliación periódica.

## 4. Reglas para los movimientos

- IN: cantidad positiva; saldo posterior igual al anterior más cantidad.
- OUT: cantidad positiva; saldo posterior igual al anterior menos cantidad, sin permitir negativos.
- ADJUSTMENT: cantidad positiva y dirección explícita INCREASE o DECREASE.
- El motivo es obligatorio.
- El proveedor es opcional y se espera principalmente en entradas.
- Los movimientos confirmados son append-only; las correcciones se hacen mediante un nuevo movimiento compensatorio.
- La clave de idempotencia es opcional para operaciones no reintentables, pero se recomienda exigirla en el endpoint de escritura.

## 5. Consideraciones de privacidad y retención

No almacenar contraseñas, tokens ni secretos en `audit_events.details`. Los datos de contacto de proveedores se limitan a los necesarios para la operación. La retención y eliminación de datos personales deberá ajustarse a las obligaciones aplicables y a la política del comercio.

## 6. Pendientes de negocio

Antes de generar la migración definitiva deben validarse: unicidad de referencias por tienda, catálogo de tallas y colores, necesidad de aprobación de ajustes, uso de códigos de barras y eventual multiubicación.
