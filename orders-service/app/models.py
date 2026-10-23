"""Order table and the shapes of data the API accepts and returns."""

from datetime import UTC, datetime
from enum import StrEnum

from sqlmodel import Field, SQLModel


class OrderStatus(StrEnum):
    PENDING = "pending"
    OUT_FOR_DELIVERY = "out_for_delivery"
    DELIVERED = "delivered"


class Order(SQLModel, table=True):
    """A row in the `order` table."""

    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    item: str
    delivery_address: str
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class OrderCreate(SQLModel):
    """What a client sends to place an order."""

    user_id: int = Field(gt=0)
    item: str = Field(min_length=1, max_length=100)


class OrderRead(SQLModel):
    """What the API sends back."""

    id: int
    user_id: int
    item: str
    delivery_address: str
    status: OrderStatus
    created_at: datetime


class OrderStatusUpdate(SQLModel):
    status: OrderStatus
