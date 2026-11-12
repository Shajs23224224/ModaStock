import uuid
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.db_session import get_db
from app.models import Category, Color, InventoryBalance, Product, ProductVariant, Size, User
from app.auth import get_current_user, require_roles
from app.schemas import ProductCreate, ProductRead, StockRead, VariantCreate, VariantRead
router=APIRouter(tags=["Catálogo"])
@router.post("/products",response_model=ProductRead,status_code=201)
def create_product(payload:ProductCreate,db:Session=Depends(get_db),_user:User=Depends(require_roles("ADMIN","MANAGER"))):
    if payload.category_id and not db.get(Category,payload.category_id): raise HTTPException(404,"Categoría inexistente")
    item=Product(**payload.model_dump()); db.add(item)
    try: db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409,"Referencia de producto duplicada") from None
    db.refresh(item); return item
@router.get("/products",response_model=list[ProductRead])
def list_products(limit:int=Query(50,ge=1,le=100),offset:int=Query(0,ge=0),db:Session=Depends(get_db),_user:User=Depends(get_current_user)):
    return db.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.name).limit(limit).offset(offset)).all()
@router.get("/products/{product_id}",response_model=ProductRead)
def get_product(product_id:uuid.UUID,db:Session=Depends(get_db),_user:User=Depends(get_current_user)):
    item=db.get(Product,product_id)
    if not item or not item.is_active: raise HTTPException(404,"Producto no encontrado")
    return item
@router.post("/products/{product_id}/variants",response_model=VariantRead,status_code=201)
def create_variant(product_id:uuid.UUID,payload:VariantCreate,db:Session=Depends(get_db),_user:User=Depends(require_roles("ADMIN","MANAGER"))):
    product,size,color=db.get(Product,product_id),db.get(Size,payload.size_id),db.get(Color,payload.color_id)
    if not product or not product.is_active: raise HTTPException(404,"Producto no encontrado")
    if not size or not size.is_active or not color or not color.is_active: raise HTTPException(422,"Talla o color inexistente/inactivo")
    variant=ProductVariant(product_id=product_id,**payload.model_dump(exclude={"minimum_quantity"})); db.add(variant)
    try:
        db.flush(); db.add(InventoryBalance(variant_id=variant.id,quantity=0,minimum_quantity=payload.minimum_quantity)); db.commit()
    except IntegrityError:
        db.rollback(); raise HTTPException(409,"SKU, código de barras o combinación duplicada") from None
    db.refresh(variant); return variant
@router.get("/variants/{variant_id}/stock",response_model=StockRead)
def get_stock(variant_id:uuid.UUID,db:Session=Depends(get_db),_user:User=Depends(get_current_user)):
    b=db.scalar(select(InventoryBalance).where(InventoryBalance.variant_id==variant_id))
    if not b: raise HTTPException(404,"Existencia no encontrada")
    return StockRead(variant_id=variant_id,quantity=b.quantity,minimum_quantity=b.minimum_quantity,low_stock=b.quantity<=b.minimum_quantity)
