from fastapi.testclient import TestClient

AMA = {"name": "Ama", "phone": "0241234567", "address": "12 Oxford St, Osu"}


def test_health(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_user(client: TestClient) -> None:
    response = client.post("/users", json=AMA)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "Ama"


def test_list_users_starts_empty(client: TestClient) -> None:
    assert client.get("/users").json() == []


def test_list_users_after_create(client: TestClient) -> None:
    client.post("/users", json=AMA)

    users = client.get("/users").json()

    assert len(users) == 1
    assert users[0]["phone"] == AMA["phone"]


def test_get_user(client: TestClient) -> None:
    user_id = client.post("/users", json=AMA).json()["id"]

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 200
    assert response.json()["address"] == AMA["address"]


def test_get_missing_user_returns_404(client: TestClient) -> None:
    response = client.get("/users/999")

    assert response.status_code == 404


def test_create_user_rejects_empty_name(client: TestClient) -> None:
    response = client.post("/users", json={**AMA, "name": ""})

    assert response.status_code == 422


def test_create_user_rejects_short_phone(client: TestClient) -> None:
    response = client.post("/users", json={**AMA, "phone": "123"})

    assert response.status_code == 422
