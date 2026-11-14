"""Idempotent bootstrap for an optional demo account and apparel catalog.

Set DEMO_ACCOUNT_PASSWORD in the deployment environment to enable it.
The public registration endpoint remains STAFF-only.
"""
import os

from sqlalchemy import func, select

from app.db_session import get_session_factory
from app.models import (
    Category,
    Color,
    InventoryBalance,
    InventoryMovement,
    Product,
    ProductVariant,
    Role,
    Size,
    User,
)
from app.security import hash_password

DEMO_EMAIL = os.getenv("DEMO_ACCOUNT_EMAIL", "demo@modastock.app").strip().lower()
DEMO_NAME = os.getenv("DEMO_ACCOUNT_NAME", "Cuenta de demostración").strip()
DEMO_PASSWORD = os.getenv("DEMO_ACCOUNT_PASSWORD", "")

CATEGORIES = {
    "Camisetas": "Camisetas y prendas superiores.",
    "Camisas": "Camisas casuales.",
    "Pantalones": "Pantalones y denim.",
    "Buzos": "Buzos y prendas exteriores.",
}
SIZES = [("S", 1), ("M", 2), ("L", 3), ("32", 4)]
COLORS = [
    ("Negro", "#171717"),
    ("Blanco", "#FFFFFF"),
    ("Beige", "#D8C3A5"),
    ("Azul", "#315A8A"),
    ("Gris", "#808080"),
]

PRODUCTS = [
    {
        "name": "Camiseta básica oversize",
        "reference": "DEMO-CAM-001",
        "description": "Camiseta unisex de algodón, corte oversize.",
        "category": "Camisetas",
        "variants": [("M", "Negro", "DEMO-CAM001-M-NEG", 18), ("L", "Blanco", "DEMO-CAM001-L-BLA", 12)],
    },
    {
        "name": "Camisa de lino",
        "reference": "DEMO-CAM-002",
        "description": "Camisa ligera de lino para uso casual.",
        "category": "Camisas",
        "variants": [("M", "Beige", "DEMO-CAM002-M-BEI", 9)],
    },
    {
        "name": "Jean recto clásico",
        "reference": "DEMO-JEA-001",
        "description": "Jean de corte recto en denim azul.",
        "category": "Pantalones",
        "variants": [("32", "Azul", "DEMO-JEA001-32-AZU", 14)],
    },
    {
        "name": "Hoodie urbano",
        "reference": "DEMO-HOO-001",
        "description": "Buzo con capota de ajuste cómodo.",
        "category": "Buzos",
        "variants": [("M", "Gris", "DEMO-HOO001-M-GRI", 7)],
    },
]


def seed_demo() -> None:
    if not DEMO_PASSWORD:
        print("Demo seed skipped: DEMO_ACCOUNT_PASSWORD is not configured.")
        return
    if len(DEMO_PASSWORD) < 12:
        raise ValueError("DEMO_ACCOUNT_PASSWORD must contain at least 12 characters.")
    if not DEMO_EMAIL or not DEMO_NAME:
        raise ValueError("Demo account email and name must not be empty.")

    db = get_session_factory()()
    try:
        manager_role = db.scalar(select(Role).where(Role.name == "MANAGER"))
        if manager_role is None:
            raise RuntimeError("Roles are not initialized; run app.seed_roles first.")

        user = db.scalar(
            select(User).where(func.lower(User.email) == DEMO_EMAIL)
        )
        if user is None:
            user = User(
                role_id=manager_role.id,
                email=DEMO_EMAIL,
                full_name=DEMO_NAME,
                password_hash=hash_password(DEMO_PASSWORD),
            )
            db.add(user)
            db.flush()
        else:
            # Only the explicitly configured demo account receives manager access.
            user.role_id = manager_role.id
            user.is_active = True

        category_rows = {}
        for name, description in CATEGORIES.items():
            category = db.scalar(select(Category).where(Category.name == name))
            if category is None:
                category = Category(name=name, description=description)
                db.add(category)
                db.flush()
            category_rows[name] = category

        size_rows = {}
        for name, order in SIZES:
            size = db.scalar(select(Size).where(Size.name == name))
            if size is None:
                size = Size(name=name, sort_order=order)
                db.add(size)
                db.flush()
            size_rows[name] = size

        color_rows = {}
        for name, hex_code in COLORS:
            color = db.scalar(select(Color).where(Color.name == name))
            if color is None:
                color = Color(name=name, hex_code=hex_code)
                db.add(color)
                db.flush()
            color_rows[name] = color

        for item in PRODUCTS:
            product = db.scalar(
                select(Product).where(Product.model_reference == item["reference"])
            )
            if product is None:
                product = Product(
                    name=item["name"],
                    model_reference=item["reference"],
                    description=item["description"],
                    category_id=category_rows[item["category"]].id,
                )
                db.add(product)
                db.flush()

            for size_name, color_name, sku, opening_quantity in item["variants"]:
                variant = db.scalar(select(ProductVariant).where(ProductVariant.sku == sku))
                if variant is None:
                    variant = ProductVariant(
                        product_id=product.id,
                        size_id=size_rows[size_name].id,
                        color_id=color_rows[color_name].id,
                        sku=sku,
                    )
                    db.add(variant)
                    db.flush()
                    db.add(
                        InventoryBalance(
                            variant_id=variant.id,
                            quantity=0,
                            minimum_quantity=3,
                        )
                    )
                    db.flush()

                balance = db.scalar(
                    select(InventoryBalance).where(
                        InventoryBalance.variant_id == variant.id
                    )
                )
                if balance is None:
                    balance = InventoryBalance(
                        variant_id=variant.id,
                        quantity=0,
                        minimum_quantity=3,
                    )
                    db.add(balance)
                    db.flush()

                movement_key = f"demo-opening-{sku}"
                movement = db.scalar(
                    select(InventoryMovement).where(
                        InventoryMovement.idempotency_key == movement_key
                    )
                )
                if movement is None:
                    before = balance.quantity
                    after = before + opening_quantity
                    balance.quantity = after
                    db.add(
                        InventoryMovement(
                            variant_id=variant.id,
                            user_id=user.id,
                            movement_type="IN",
                            quantity=opening_quantity,
                            stock_before=before,
                            stock_after=after,
                            reason="Carga inicial de inventario de demostración",
                            reference=f"DEMO-{sku}",
                            idempotency_key=movement_key,
                        )
                    )

        db.commit()
        print(
            f"Demo seed ready: {DEMO_EMAIL}; "
            f"{len(PRODUCTS)} products and "
            f"{sum(len(item['variants']) for item in PRODUCTS)} variants."
        )
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo()
