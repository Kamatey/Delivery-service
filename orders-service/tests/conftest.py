"""Shared test fixtures: a fresh in-memory database and a fake users service."""

from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.database import get_session
from app.main import app
from app.users_client import (
    UserNotFoundError,
    UsersServiceUnavailableError,
    get_user_fetcher,
)

FAKE_USERS = {1: {"id": 1, "name": "Ama", "address": "12 Oxford St, Osu"}}


def fake_fetch_user(user_id: int) -> dict[str, Any]:
    if user_id not in FAKE_USERS:
        raise UserNotFoundError(user_id)
    return FAKE_USERS[user_id]


def unreachable_fetch_user(user_id: int) -> dict[str, Any]:
    raise UsersServiceUnavailableError


@pytest.fixture
def session() -> Generator[Session]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def client(session: Session) -> Generator[TestClient]:
    # Swap the real database and the real users service for test doubles,
    # so these tests run without Docker or a network.
    app.dependency_overrides[get_session] = lambda: session
    app.dependency_overrides[get_user_fetcher] = lambda: fake_fetch_user
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_users_down(client: TestClient) -> TestClient:
    app.dependency_overrides[get_user_fetcher] = lambda: unreachable_fetch_user
    return client
