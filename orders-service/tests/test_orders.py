"""API tests for the orders endpoints."""

from fastapi.testclient import TestClient

ORDER = {"user_id": 1, "item": "Jollof rice"}


def test_health(client: TestClient) -> None:
    assert client.get("/health").json()["status"] == "ok"


def test_create_order_uses_users_address(client: TestClient) -> None:
    response = client.post("/orders", json=ORDER)

    assert response.status_code == 201
    body = response.json()
    assert body["status"] == "pending"
    assert body["delivery_address"] == "12 Oxford St, Osu"


def test_create_order_for_unknown_user_returns_400(client: TestClient) -> None:
    response = client.post("/orders", json={**ORDER, "user_id": 99})

    assert response.status_code == 400


def test_create_order_when_users_service_down_returns_503(
    client_users_down: TestClient,
) -> None:
    response = client_users_down.post("/orders", json=ORDER)

    assert response.status_code == 503


def test_create_order_rejects_empty_item(client: TestClient) -> None:
    response = client.post("/orders", json={**ORDER, "item": ""})

    assert response.status_code == 422


def test_list_orders_filters_by_user(client: TestClient) -> None:
    client.post("/orders", json=ORDER)

    assert len(client.get("/orders", params={"user_id": 1}).json()) == 1
    assert client.get("/orders", params={"user_id": 2}).json() == []


def test_get_missing_order_returns_404(client: TestClient) -> None:
    assert client.get("/orders/999").status_code == 404


def test_order_moves_through_delivery(client: TestClient) -> None:
    order_id = client.post("/orders", json=ORDER).json()["id"]

    for new_status in ("out_for_delivery", "delivered"):
        response = client.patch(
            f"/orders/{order_id}/status", json={"status": new_status}
        )
        assert response.status_code == 200
        assert response.json()["status"] == new_status


def test_order_cannot_skip_delivery_step(client: TestClient) -> None:
    order_id = client.post("/orders", json=ORDER).json()["id"]

    response = client.patch(f"/orders/{order_id}/status", json={"status": "delivered"})

    assert response.status_code == 409
