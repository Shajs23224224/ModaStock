from types import SimpleNamespace
import uuid

import pytest
from pydantic import ValidationError

from app.inventory import _same_operation
from app.schemas import MovementCreate


def test_adjustment_requires_direction_and_other_movements_forbid_it():
    variant_id = uuid.uuid4()
    with pytest.raises(ValidationError):
        MovementCreate(variant_id=variant_id, movement_type="ADJUSTMENT", quantity=2, reason="Conteo")
    with pytest.raises(ValidationError):
        MovementCreate(variant_id=variant_id, movement_type="IN", quantity=2, reason="Recepción", adjustment_direction="INCREASE")
    valid = MovementCreate(variant_id=variant_id, movement_type="ADJUSTMENT", quantity=2, reason="Conteo", adjustment_direction="DECREASE")
    assert valid.adjustment_direction == "DECREASE"


def test_idempotency_match_checks_full_operation_identity():
    variant_id, user_id, supplier_id = uuid.uuid4(), uuid.uuid4(), uuid.uuid4()
    payload = MovementCreate(
        variant_id=variant_id, movement_type="IN", quantity=4,
        reason=" Recepción ", supplier_id=supplier_id, reference="OC-15"
    )
    existing = SimpleNamespace(
        variant_id=variant_id, user_id=user_id, movement_type="IN",
        adjustment_direction=None, quantity=4, reason="Recepción",
        supplier_id=supplier_id, reference="OC-15"
    )
    assert _same_operation(existing, payload, user_id)
    assert not _same_operation(existing, payload, uuid.uuid4())
    existing.reference = "OC-16"
    assert not _same_operation(existing, payload, user_id)


def test_movement_rejects_non_positive_quantity():
    with pytest.raises(ValidationError):
        MovementCreate(variant_id=uuid.uuid4(), movement_type="OUT", quantity=0, reason="Venta")
