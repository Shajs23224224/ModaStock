import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db_session import get_db
from app.models import Category, Color, InventoryBalance, InventoryMovement, Product, ProductVariant, Size, User
from app.auth import get_current_user, require_roles
from app.schemas import (
    ColorRead, MinimumStockUpdate, MovementRead, ProductCreate, ProductRead,
    SizeRead, StockRead, VariantCreate, VariantInventoryRead, VariantRead,
)

router = APIRouter(tags=["Catálogo e inventario"])

@router.post("/products", response_model=ProductRead, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db), _user: User = Depends(require_roles("ADMIN", "MANAGER"))):
    if payload.category_id and not db.get(Category, payload.category_id):
        raise HTTPException(404, "Categoría inexistente")
    item = Product(**payload.model_dump())
    db.add(item)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "Referencia de producto duplicada") from None
    db.refresh(item)
    return item

@router.get("/products", response_model=list[ProductRead])
def list_products(limit: int = Query(50, ge=1, le=100), offset: int = Query(0, ge=0), db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.name).limit(limit).offset(offset)).all()

@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: uuid.UUID, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    item = db.get(Product, product_id)
    if not item or not item.is_active:
        raise HTTPException(404, "Producto no encontrado")
    return item

@router.post("/products/{product_id}/variants", response_model=VariantRead, status_code=201)
def create_variant(product_id: uuid.UUID, payload: VariantCreate, db: Session = Depends(get_db), _user: User = Depends(require_roles("ADMIN", "MANAGER"))):
    product, size, color = db.get(Product, product_id), db.get(Size, payload.size_id), db.get(Color, payload.color_id)
    if not product or not product.is_active:
        raise HTTPException(404, "Producto no encontrado")
    if not size or not size.is_active or not color or not color.is_active:
        raise HTTPException(422, "Talla o color inexistente/inactivo")
    variant = ProductVariant(product_id=product_id, **payload.model_dump(exclude={"minimum_quantity"}))
    db.add(variant)
    try:
        db.flush()
        db.add(InventoryBalance(variant_id=variant.id, quantity=0, minimum_quantity=payload.minimum_quantity))
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, "SKU, código de barras o combinación duplicada") from None
    db.refresh(variant)
    return variant

@router.get("/sizes", response_model=list[SizeRead])
def list_sizes(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.scalars(select(Size).where(Size.is_active.is_(True)).order_by(Size.sort_order, Size.name)).all()

@router.get("/colors", response_model=list[ColorRead])
def list_colors(db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    return db.scalars(select(Color).where(Color.is_active.is_(True)).order_by(Color.name)).all()

def _query_variants(
    db: Session,
    q: str | None,
    product_id: uuid.UUID | None,
    low_stock_only: bool,
    limit: int,
    offset: int,
):
    stmt = (
        select(ProductVariant, Product, Size, Color, InventoryBalance)
        .join(Product, Product.id == ProductVariant.product_id)
        .join(Size, Size.id == ProductVariant.size_id)
        .join(Color, Color.id == ProductVariant.color_id)
        .join(InventoryBalance, InventoryBalance.variant_id == ProductVariant.id)
        .where(ProductVariant.is_active.is_(True), Product.is_active.is_(True))
    )
    if product_id:
        stmt = stmt.where(ProductVariant.product_id == product_id)
    if q and q.strip():
        term = f"%{q.strip()}%"
        stmt = stmt.where(or_(ProductVariant.sku.ilike(term), Product.name.ilike(term), Product.model_reference.ilike(term), Size.name.ilike(term), Color.name.ilike(term)))
    if low_stock_only:
        stmt = stmt.where(InventoryBalance.quantity <= InventoryBalance.minimum_quantity)
    rows = db.execute(stmt.order_by(Product.name, ProductVariant.sku).limit(limit).offset(offset)).all()
    return [
        VariantInventoryRead(
            id=v.id, product_id=p.id, product_name=p.name, model_reference=p.model_reference,
            size_id=s.id, size_name=s.name, color_id=c.id, color_name=c.name,
            sku=v.sku, barcode=v.barcode, is_active=v.is_active,
            quantity=b.quantity, minimum_quantity=b.minimum_quantity,
            low_stock=b.quantity <= b.minimum_quantity,
        )
        for v, p, s, c, b in rows
    ]


@router.get("/variants", response_model=list[VariantInventoryRead])
def list_variants(
    q: str | None = Query(default=None, max_length=100),
    product_id: uuid.UUID | None = None,
    low_stock_only: bool = False,
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return _query_variants(db, q, product_id, low_stock_only, limit, offset)

@router.get("/variants/{variant_id}/stock", response_model=StockRead)
def get_stock(variant_id: uuid.UUID, db: Session = Depends(get_db), _user: User = Depends(get_current_user)):
    balance = db.scalar(select(InventoryBalance).where(InventoryBalance.variant_id == variant_id))
    if not balance:
        raise HTTPException(404, "Existencia no encontrada")
    return StockRead(variant_id=variant_id, quantity=balance.quantity, minimum_quantity=balance.minimum_quantity, low_stock=balance.quantity <= balance.minimum_quantity)

@router.patch("/variants/{variant_id}/minimum-stock", response_model=StockRead)
def update_minimum_stock(variant_id: uuid.UUID, payload: MinimumStockUpdate, db: Session = Depends(get_db), _user: User = Depends(require_roles("ADMIN", "MANAGER"))):
    balance = db.scalar(select(InventoryBalance).where(InventoryBalance.variant_id == variant_id).with_for_update())
    if not balance:
        raise HTTPException(404, "Existencia no encontrada")
    balance.minimum_quantity = payload.minimum_quantity
    db.commit()
    db.refresh(balance)
    return StockRead(variant_id=variant_id, quantity=balance.quantity, minimum_quantity=balance.minimum_quantity, low_stock=balance.quantity <= balance.minimum_quantity)

@router.get("/inventory/stock", response_model=list[VariantInventoryRead])
def list_stock(
    low_stock_only: bool = False,
    q: str | None = Query(default=None, max_length=100),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return _query_variants(db, q, None, low_stock_only, limit, offset)

@router.get("/inventory/movements", response_model=list[MovementRead])
def list_movements(
    variant_id: uuid.UUID | None = None,
    movement_type: str | None = Query(default=None, pattern="^(IN|OUT|ADJUSTMENT)$"),
    limit: int = Query(100, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    stmt = select(InventoryMovement)
    if variant_id:
        stmt = stmt.where(InventoryMovement.variant_id == variant_id)
    if movement_type:
        stmt = stmt.where(InventoryMovement.movement_type == movement_type)
    return db.scalars(stmt.order_by(InventoryMovement.created_at.desc(), InventoryMovement.id.desc()).limit(limit).offset(offset)).all()
