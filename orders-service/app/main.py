"""Orders service: places orders and tracks their delivery status."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlmodel import Session, select

from app.database import create_db_and_tables, get_session
from app.delivery import can_change_status
from app.models import Order, OrderCreate, OrderRead, OrderStatusUpdate
from app.users_client import (
    UserFetcher,
    UserNotFoundError,
    UsersServiceUnavailableError,
    get_user_fetcher,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


app = FastAPI(title="Orders Service", version="1.0.0", lifespan=lifespan)

SessionDep = Annotated[Session, Depends(get_session)]
UserFetcherDep = Annotated[UserFetcher, Depends(get_user_fetcher)]


def get_order_or_404(order_id: int, session: Session) -> Order:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail="Order not found")
    return order


@app.get("/health")
def health() -> dict[str, str]:
    return {"service": "orders", "status": "ok"}


@app.post("/orders", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate, session: SessionDep, fetch_user: UserFetcherDep
) -> Order:
    # Ask the users service who this customer is and where to deliver.
    try:
        user = fetch_user(order_in.user_id)
    except UserNotFoundError:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST, detail="That user does not exist"
        ) from None
    except UsersServiceUnavailableError:
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE, detail="Users service is unreachable"
        ) from None

    order = Order(
        user_id=order_in.user_id,
        item=order_in.item,
        delivery_address=user["address"],
    )
    session.add(order)
    session.commit()
    session.refresh(order)
    return order


@app.get("/orders", response_model=list[OrderRead])
def list_orders(session: SessionDep, user_id: int | None = None) -> list[Order]:
    query = select(Order)
    if user_id is not None:
        query = query.where(Order.user_id == user_id)
    return list(session.exec(query).all())


@app.get("/orders/{order_id}", response_model=OrderRead)
def get_order(order_id: int, session: SessionDep) -> Order:
    return get_order_or_404(order_id, session)


@app.patch("/orders/{order_id}/status", response_model=OrderRead)
def update_order_status(
    order_id: int, update: OrderStatusUpdate, session: SessionDep
) -> Order:
    order = get_order_or_404(order_id, session)
    if not can_change_status(order.status, update.status):
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            detail=f"Cannot move order from {order.status} to {update.status}",
        )

    order.status = update.status
    session.add(order)
    session.commit()
    session.refresh(order)
    return order
