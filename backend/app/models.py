import uuid
from datetime import datetime
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Index, Integer, JSON, String, Text, UniqueConstraint, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db_base import Base
class Role(Base):
    __tablename__="roles"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(50),unique=True)
    description: Mapped[str|None]=mapped_column(Text)
class User(Base):
    __tablename__="users"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    role_id: Mapped[uuid.UUID]=mapped_column(Uuid,ForeignKey("roles.id",ondelete="RESTRICT"))
    email: Mapped[str]=mapped_column(String(254),nullable=False)
    password_hash: Mapped[str]=mapped_column(String(255),nullable=False)
    full_name: Mapped[str]=mapped_column(String(150),nullable=False)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    __table_args__=(Index("uq_users_email_lower",func.lower(email),unique=True),)
class Category(Base):
    __tablename__="categories"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(100),unique=True)
    description: Mapped[str|None]=mapped_column(Text)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class Product(Base):
    __tablename__="products"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    category_id: Mapped[uuid.UUID|None]=mapped_column(Uuid,ForeignKey("categories.id",ondelete="RESTRICT"))
    name: Mapped[str]=mapped_column(String(150),nullable=False)
    model_reference: Mapped[str]=mapped_column(String(80),unique=True,nullable=False)
    description: Mapped[str|None]=mapped_column(Text)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
class Size(Base):
    __tablename__="sizes"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(30),unique=True)
    sort_order: Mapped[int]=mapped_column(Integer,default=0)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
class Color(Base):
    __tablename__="colors"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(60),unique=True)
    hex_code: Mapped[str|None]=mapped_column(String(7))
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    __table_args__=(CheckConstraint("hex_code IS NULL OR (length(hex_code)=7 AND substr(hex_code,1,1)='#')",name="ck_colors_hex_code"),)
class ProductVariant(Base):
    __tablename__="product_variants"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    product_id: Mapped[uuid.UUID]=mapped_column(Uuid,ForeignKey("products.id",ondelete="RESTRICT"))
    size_id: Mapped[uuid.UUID]=mapped_column(Uuid,ForeignKey("sizes.id",ondelete="RESTRICT"))
    color_id: Mapped[uuid.UUID]=mapped_column(Uuid,ForeignKey("colors.id",ondelete="RESTRICT"))
    sku: Mapped[str]=mapped_column(String(100),unique=True)
    barcode: Mapped[str|None]=mapped_column(String(64),unique=True)
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    __table_args__=(UniqueConstraint("product_id","size_id","color_id",name="uq_variant_product_size_color"),)
class InventoryBalance(Base):
    __tablename__="inventory_balances"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    variant_id: Mapped[uuid.UUID]=mapped_column(Uuid,ForeignKey("product_variants.id",ondelete="RESTRICT"),unique=True)
    quantity: Mapped[int]=mapped_column(Integer,default=0)
    minimum_quantity: Mapped[int]=mapped_column(Integer,default=0)
    updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now(),onupdate=func.now())
    __table_args__=(CheckConstraint("quantity>=0",name="ck_balance_quantity_nonnegative"),CheckConstraint("minimum_quantity>=0",name="ck_balance_minimum_nonnegative"))
class Supplier(Base):
    __tablename__="suppliers"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    name: Mapped[str]=mapped_column(String(150))
    contact_name: Mapped[str|None]=mapped_column(String(150))
    email: Mapped[str|None]=mapped_column(String(254))
    phone: Mapped[str|None]=mapped_column(String(40))
    is_active: Mapped[bool]=mapped_column(Boolean,default=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
class InventoryMovement(Base):
    __tablename__="inventory_movements"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    variant_id: Mapped[uuid.UUID]=mapped_column(Uuid,ForeignKey("product_variants.id",ondelete="RESTRICT"))
    user_id: Mapped[uuid.UUID]=mapped_column(Uuid,ForeignKey("users.id",ondelete="RESTRICT"))
    supplier_id: Mapped[uuid.UUID|None]=mapped_column(Uuid,ForeignKey("suppliers.id",ondelete="RESTRICT"))
    movement_type: Mapped[str]=mapped_column(String(12))
    adjustment_direction: Mapped[str|None]=mapped_column(String(8))
    quantity: Mapped[int]=mapped_column(Integer)
    stock_before: Mapped[int]=mapped_column(Integer)
    stock_after: Mapped[int]=mapped_column(Integer)
    reason: Mapped[str]=mapped_column(String(250))
    reference: Mapped[str|None]=mapped_column(String(100))
    idempotency_key: Mapped[str|None]=mapped_column(String(100))
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
    __table_args__=(CheckConstraint("movement_type IN ('IN','OUT','ADJUSTMENT')",name="ck_movement_type"),CheckConstraint("(movement_type='ADJUSTMENT' AND adjustment_direction IN ('INCREASE','DECREASE')) OR (movement_type IN ('IN','OUT') AND adjustment_direction IS NULL)",name="ck_adjustment_direction"),CheckConstraint("quantity>0 AND stock_before>=0 AND stock_after>=0",name="ck_movement_quantities"),CheckConstraint("(movement_type='IN' AND stock_after=stock_before+quantity) OR (movement_type='OUT' AND stock_after=stock_before-quantity) OR (movement_type='ADJUSTMENT' AND ((adjustment_direction='INCREASE' AND stock_after=stock_before+quantity) OR (adjustment_direction='DECREASE' AND stock_after=stock_before-quantity)))",name="ck_movement_stock_math"),Index("uq_inventory_movements_idempotency","idempotency_key",unique=True,postgresql_where=idempotency_key.is_not(None)))
class AuditEvent(Base):
    __tablename__="audit_events"
    id: Mapped[uuid.UUID]=mapped_column(Uuid,primary_key=True,default=uuid.uuid4)
    user_id: Mapped[uuid.UUID|None]=mapped_column(Uuid,ForeignKey("users.id",ondelete="SET NULL"))
    action: Mapped[str]=mapped_column(String(80))
    entity_type: Mapped[str]=mapped_column(String(80))
    entity_id: Mapped[uuid.UUID|None]=mapped_column(Uuid)
    details: Mapped[dict]=mapped_column(JSON,default=dict)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),server_default=func.now())
