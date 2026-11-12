from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import InventoryBalance,InventoryMovement,ProductVariant
from app.schemas import MovementCreate
def register_movement(db:Session,payload:MovementCreate,idempotency_key:str|None=None):
    if idempotency_key:
        previous=db.scalar(select(InventoryMovement).where(InventoryMovement.idempotency_key==idempotency_key))
        if previous:
            if (previous.variant_id,previous.movement_type,previous.quantity)!=(payload.variant_id,payload.movement_type,payload.quantity):
                raise HTTPException(409,"Clave idempotente reutilizada con otra operación")
            return previous
    try:
        variant=db.scalar(select(ProductVariant).where(ProductVariant.id==payload.variant_id).with_for_update())
        balance=db.scalar(select(InventoryBalance).where(InventoryBalance.variant_id==payload.variant_id).with_for_update())
        if not variant or not variant.is_active: raise HTTPException(404,"Variante inexistente o inactiva")
        if not balance: raise HTTPException(409,"Saldo no inicializado")
        before=balance.quantity
        increase=payload.movement_type=="IN" or (payload.movement_type=="ADJUSTMENT" and payload.adjustment_direction=="INCREASE")
        after=before+payload.quantity if increase else before-payload.quantity
        if after<0: raise HTTPException(409,"Existencias insuficientes")
        movement=InventoryMovement(variant_id=payload.variant_id,user_id=payload.user_id,supplier_id=payload.supplier_id,movement_type=payload.movement_type,adjustment_direction=payload.adjustment_direction,quantity=payload.quantity,stock_before=before,stock_after=after,reason=payload.reason.strip(),reference=payload.reference,idempotency_key=idempotency_key)
        balance.quantity=after; db.add(movement); db.commit(); db.refresh(movement); return movement
    except IntegrityError:
        db.rollback()
        if idempotency_key:
            existing=db.scalar(select(InventoryMovement).where(InventoryMovement.idempotency_key==idempotency_key))
            if existing: return existing
        raise HTTPException(409,"Conflicto de integridad") from None
    except Exception:
        db.rollback(); raise
