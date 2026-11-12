from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import InventoryBalance, InventoryMovement, ProductVariant
from app.schemas import MovementCreate

def _same_operation(existing: InventoryMovement, payload: MovementCreate, user_id) -> bool:
    return (
        existing.variant_id == payload.variant_id
        and existing.user_id == user_id
        and existing.movement_type == payload.movement_type
        and existing.adjustment_direction == payload.adjustment_direction
        and existing.quantity == payload.quantity
        and existing.reason == payload.reason.strip()
        and existing.supplier_id == payload.supplier_id
        and existing.reference == payload.reference
    )

def register_movement(db: Session, payload: MovementCreate, user_id, idempotency_key: str | None = None):
    if idempotency_key is not None:
        idempotency_key = idempotency_key.strip()
        if not idempotency_key or len(idempotency_key) > 100:
            raise HTTPException(422, "Idempotency-Key debe contener entre 1 y 100 caracteres")
        previous = db.scalar(select(InventoryMovement).where(InventoryMovement.idempotency_key == idempotency_key))
        if previous:
            if not _same_operation(previous, payload, user_id):
                raise HTTPException(409, "Clave idempotente reutilizada con otra operación")
            return previous
    try:
        variant = db.scalar(select(ProductVariant).where(ProductVariant.id == payload.variant_id).with_for_update())
        if not variant or not variant.is_active:
            raise HTTPException(404, "Variante inexistente o inactiva")
        balance = db.scalar(select(InventoryBalance).where(InventoryBalance.variant_id == payload.variant_id).with_for_update())
        if not balance:
            raise HTTPException(409, "Saldo no inicializado")
        if idempotency_key:
            previous = db.scalar(select(InventoryMovement).where(InventoryMovement.idempotency_key == idempotency_key))
            if previous:
                if not _same_operation(previous, payload, user_id):
                    raise HTTPException(409, "Clave idempotente reutilizada con otra operación")
                db.rollback()
                return previous
        before = balance.quantity
        increase = payload.movement_type == "IN" or (payload.movement_type == "ADJUSTMENT" and payload.adjustment_direction == "INCREASE")
        after = before + payload.quantity if increase else before - payload.quantity
        if after < 0:
            raise HTTPException(409, "Existencias insuficientes")
        movement = InventoryMovement(
            variant_id=payload.variant_id, user_id=user_id, supplier_id=payload.supplier_id,
            movement_type=payload.movement_type, adjustment_direction=payload.adjustment_direction,
            quantity=payload.quantity, stock_before=before, stock_after=after,
            reason=payload.reason.strip(), reference=payload.reference, idempotency_key=idempotency_key,
        )
        balance.quantity = after
        db.add(movement)
        db.commit()
        db.refresh(movement)
        return movement
    except IntegrityError:
        db.rollback()
        if idempotency_key:
            existing = db.scalar(select(InventoryMovement).where(InventoryMovement.idempotency_key == idempotency_key))
            if existing and _same_operation(existing, payload, user_id):
                return existing
            if existing:
                raise HTTPException(409, "Clave idempotente reutilizada con otra operación") from None
        raise HTTPException(409, "Conflicto de integridad al registrar el movimiento") from None
    except Exception:
        db.rollback()
        raise
