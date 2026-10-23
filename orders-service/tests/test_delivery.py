"""Pure unit tests for the delivery rules (no API, no database)."""

import pytest

from app.delivery import can_change_status
from app.models import OrderStatus


@pytest.mark.parametrize(
    ("current", "new"),
    [
        (OrderStatus.PENDING, OrderStatus.OUT_FOR_DELIVERY),
        (OrderStatus.OUT_FOR_DELIVERY, OrderStatus.DELIVERED),
    ],
)
def test_allowed_moves(current: OrderStatus, new: OrderStatus) -> None:
    assert can_change_status(current, new) is True


@pytest.mark.parametrize(
    ("current", "new"),
    [
        (OrderStatus.PENDING, OrderStatus.DELIVERED),  # cannot skip a step
        (OrderStatus.DELIVERED, OrderStatus.PENDING),  # cannot go back
        (OrderStatus.OUT_FOR_DELIVERY, OrderStatus.PENDING),
        (OrderStatus.PENDING, OrderStatus.PENDING),
    ],
)
def test_blocked_moves(current: OrderStatus, new: OrderStatus) -> None:
    assert can_change_status(current, new) is False
