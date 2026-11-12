import uuid
from datetime import datetime
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator, EmailStr
class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=150)
    password: str = Field(min_length=12, max_length=128)
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)
class TokenRead(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
class UserRead(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
class ProductCreate(BaseModel):
    name: str=Field(min_length=1,max_length=150)
    model_reference: str=Field(min_length=1,max_length=80)
    category_id: uuid.UUID|None=None
    description: str|None=None
class ProductRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: uuid.UUID
    name: str
    model_reference: str
    category_id: uuid.UUID|None
    description: str|None
    is_active: bool
    created_at: datetime
class VariantCreate(BaseModel):
    size_id: uuid.UUID
    color_id: uuid.UUID
    sku: str=Field(min_length=1,max_length=100)
    barcode: str|None=Field(default=None,max_length=64)
    minimum_quantity: int=Field(default=0,ge=0)
class VariantRead(BaseModel):
    model_config=ConfigDict(from_attributes=True)
    id: uuid.UUID
    product_id: uuid.UUID
    size_id: uuid.UUID
    color_id: uuid.UUID
    sku: str
    barcode: str|None
    is_active: bool
class StockRead(BaseModel):
    variant_id: uuid.UUID
    quantity: int
    minimum_quantity: int
    low_stock: bool
class MovementCreate(BaseModel):
    variant_id: uuid.UUID
    movement_type: Literal["IN","OUT","ADJUSTMENT"]
    quantity: int=Field(gt=0)
    reason: str=Field(min_length=1,max_length=250)
    supplier_id: uuid.UUID|None=None
    adjustment_direction: Literal["INCREASE","DECREASE"]|None=None
    reference: str|None=Field(default=None,max_length=100)
    @model_validator(mode="after")
    def check_adjustment(self):
        if (self.movement_type=="ADJUSTMENT") != (self.adjustment_direction is not None):
            raise ValueError("Dirección requerida únicamente para ajustes")
        return self
