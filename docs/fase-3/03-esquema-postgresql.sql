-- ModaStock — Fase 3
-- Esquema lógico/físico inicial propuesto para PostgreSQL.
-- No ejecutar en producción sin revisión y migración versionada con Alembic.
-- Requiere PostgreSQL con gen_random_uuid() disponible.

BEGIN;

CREATE TABLE roles (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(50) NOT NULL UNIQUE,
    description text
);

CREATE TABLE users (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    role_id uuid NOT NULL REFERENCES roles(id) ON DELETE RESTRICT,
    email varchar(254) NOT NULL,
    password_hash varchar(255) NOT NULL,
    full_name varchar(150) NOT NULL,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
);

CREATE UNIQUE INDEX uq_users_email_lower ON users (lower(email));

CREATE TABLE categories (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(100) NOT NULL UNIQUE,
    description text,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE products (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    category_id uuid REFERENCES categories(id) ON DELETE RESTRICT,
    name varchar(150) NOT NULL,
    model_reference varchar(80) NOT NULL UNIQUE,
    description text,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE sizes (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(30) NOT NULL UNIQUE,
    sort_order integer NOT NULL DEFAULT 0,
    is_active boolean NOT NULL DEFAULT true
);

CREATE TABLE colors (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(60) NOT NULL UNIQUE,
    hex_code varchar(7),
    is_active boolean NOT NULL DEFAULT true,
    CONSTRAINT ck_colors_hex_code
        CHECK (hex_code IS NULL OR hex_code ~ '^#[0-9A-Fa-f]{6}$')
);

CREATE TABLE product_variants (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id uuid NOT NULL REFERENCES products(id) ON DELETE RESTRICT,
    size_id uuid NOT NULL REFERENCES sizes(id) ON DELETE RESTRICT,
    color_id uuid NOT NULL REFERENCES colors(id) ON DELETE RESTRICT,
    sku varchar(100) NOT NULL UNIQUE,
    barcode varchar(64) UNIQUE,
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_variant_product_size_color
        UNIQUE (product_id, size_id, color_id)
);

CREATE TABLE inventory_balances (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id uuid NOT NULL UNIQUE
        REFERENCES product_variants(id) ON DELETE RESTRICT,
    quantity integer NOT NULL DEFAULT 0,
    minimum_quantity integer NOT NULL DEFAULT 0,
    updated_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_balance_quantity_nonnegative CHECK (quantity >= 0),
    CONSTRAINT ck_balance_minimum_nonnegative CHECK (minimum_quantity >= 0)
);

CREATE TABLE suppliers (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    name varchar(150) NOT NULL,
    contact_name varchar(150),
    email varchar(254),
    phone varchar(40),
    is_active boolean NOT NULL DEFAULT true,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE inventory_movements (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    variant_id uuid NOT NULL
        REFERENCES product_variants(id) ON DELETE RESTRICT,
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    supplier_id uuid REFERENCES suppliers(id) ON DELETE RESTRICT,
    movement_type varchar(12) NOT NULL,
    adjustment_direction varchar(8),
    quantity integer NOT NULL,
    stock_before integer NOT NULL,
    stock_after integer NOT NULL,
    reason varchar(250) NOT NULL,
    reference varchar(100),
    idempotency_key varchar(100),
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_movement_type
        CHECK (movement_type IN ('IN', 'OUT', 'ADJUSTMENT')),
    CONSTRAINT ck_adjustment_direction
        CHECK (
            (movement_type = 'ADJUSTMENT'
                AND adjustment_direction IS NOT NULL
                AND adjustment_direction IN ('INCREASE', 'DECREASE'))
            OR
            (movement_type IN ('IN', 'OUT')
                AND adjustment_direction IS NULL)
        ),
    CONSTRAINT ck_movement_quantity_positive CHECK (quantity > 0),
    CONSTRAINT ck_movement_stock_before_nonnegative CHECK (stock_before >= 0),
    CONSTRAINT ck_movement_stock_after_nonnegative CHECK (stock_after >= 0),
    CONSTRAINT ck_movement_stock_math
        CHECK (
            (movement_type = 'IN'
                AND stock_after = stock_before + quantity)
            OR
            (movement_type = 'OUT'
                AND stock_after = stock_before - quantity)
            OR
            (movement_type = 'ADJUSTMENT'
                AND (
                    (adjustment_direction = 'INCREASE'
                        AND stock_after = stock_before + quantity)
                    OR
                    (adjustment_direction = 'DECREASE'
                        AND stock_after = stock_before - quantity)
                ))
        )
);

CREATE UNIQUE INDEX uq_inventory_movements_idempotency
    ON inventory_movements(idempotency_key)
    WHERE idempotency_key IS NOT NULL;

CREATE TABLE audit_events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id uuid REFERENCES users(id) ON DELETE SET NULL,
    action varchar(80) NOT NULL,
    entity_type varchar(80) NOT NULL,
    entity_id uuid,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

-- Índices para relaciones y consultas frecuentes.
CREATE INDEX ix_users_role_id ON users(role_id);
CREATE INDEX ix_products_category_id ON products(category_id);
CREATE INDEX ix_variants_product_id ON product_variants(product_id);
CREATE INDEX ix_variants_size_id ON product_variants(size_id);
CREATE INDEX ix_variants_color_id ON product_variants(color_id);
CREATE INDEX ix_movements_variant_created
    ON inventory_movements(variant_id, created_at DESC);
CREATE INDEX ix_movements_user_created
    ON inventory_movements(user_id, created_at DESC);
CREATE INDEX ix_movements_supplier_created
    ON inventory_movements(supplier_id, created_at DESC)
    WHERE supplier_id IS NOT NULL;
CREATE INDEX ix_movements_created_at
    ON inventory_movements(created_at DESC);
CREATE INDEX ix_audit_entity_created
    ON audit_events(entity_type, entity_id, created_at DESC);
CREATE INDEX ix_audit_user_created
    ON audit_events(user_id, created_at DESC)
    WHERE user_id IS NOT NULL;

COMMIT;

-- IMPORTANTE:
-- 1. El esquema no crea por sí solo un saldo inicial: toda carga inicial debe
--    registrarse como movimiento IN dentro de una transacción.
-- 2. La aplicación debe bloquear la fila inventory_balances (SELECT ... FOR UPDATE)
--    antes de calcular stock_after y escribir saldo + movimiento.
-- 3. La creación de variante debe crear su fila de saldo en la misma transacción.
-- 4. Debe restringirse UPDATE/DELETE de movimientos mediante permisos de DB y/o
--    controles de aplicación; correcciones con movimientos compensatorios.
-- 5. Las reglas que dependen de otras filas (p. ej. igualdad entre balance actual
--    y último movimiento) se verifican con transacciones y reconciliación, no con CHECK.
