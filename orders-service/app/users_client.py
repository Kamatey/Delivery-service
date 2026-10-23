"""Talks to the users service over HTTP (service-to-service communication)."""

import os
from collections.abc import Callable
from typing import Any

import httpx

# In Docker Compose, "users-service" is the hostname of the other container.
USERS_URL = os.getenv("USERS_URL", "http://localhost:8001")

UserFetcher = Callable[[int], dict[str, Any]]


class UserNotFoundError(Exception):
    pass


class UsersServiceUnavailableError(Exception):
    pass


def fetch_user(user_id: int) -> dict[str, Any]:
    try:
        response = httpx.get(f"{USERS_URL}/users/{user_id}", timeout=5)
    except httpx.RequestError as exc:
        raise UsersServiceUnavailableError from exc

    if response.status_code == httpx.codes.NOT_FOUND:
        raise UserNotFoundError(user_id)
    response.raise_for_status()
    return response.json()


def get_user_fetcher() -> UserFetcher:
    """FastAPI dependency, so tests can swap in a fake users service."""
    return fetch_user
