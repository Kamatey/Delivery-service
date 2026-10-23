# Ashclass Delivery

A small food-delivery backend built as **microservices**: independent services
that each do one job and work together over HTTP.

## Goal

This is my hands-on learning project. Every topic I learn in class gets built into
it, and the main focus is **microservice architecture**: how to split a system into
services, how they talk to each other, and how they keep running when one fails.

## The microservices

```
                 ┌────────────────────┐
   client ──────►│   users-service    │──► users.db
     │           │      :8001         │
     │           └─────────▲──────────┘
     │                     │  HTTP: "who is user 1, where do they live?"
     │           ┌─────────┴──────────┐
     └──────────►│   orders-service   │──► orders.db
                 │      :8002         │
                 └────────────────────┘
```

| Service | Its one job |
|---|---|
| **users-service** | Stores customers and their delivery addresses |
| **orders-service** | Takes orders and tracks delivery (`pending` → `out_for_delivery` → `delivered`) |

The microservice ideas this project practises:

- **One job per service.** Users and orders are separate apps, each with its own code.
- **Each service owns its data.** Every service has its own SQLite database.
  orders-service never reads `users.db` directly.
- **Services talk over HTTP.** When an order comes in, orders-service calls
  users-service to check the customer exists and to get their address.
- **Each service runs in its own container.** Docker Compose starts them
  together on a private network, where they find each other by name
  (`http://users-service:8000`).
- **Failures stay contained.** If users-service goes down, orders-service keeps
  running and replies `503 Users service is unreachable` instead of crashing.

**Built with:** FastAPI · SQLite (SQLModel) · uv · Docker · pytest · Ruff · GitHub Actions

## How to run

You need [Docker Desktop](https://www.docker.com/products/docker-desktop/).

```bash
docker compose up --build
```

Then open the interactive API pages:

- Users: http://localhost:8001/docs
- Orders: http://localhost:8002/docs

Try the services working together:

1. In **Users**, `POST /users` with `{"name": "Ama", "phone": "0241234567", "address": "12 Oxford St, Osu"}`
2. In **Orders**, `POST /orders` with `{"user_id": 1, "item": "Jollof rice"}`.
   The order picks up Ama's address from users-service.
3. Stop one service with `docker compose stop users-service` and place another
   order. Orders still answers, with a 503 error.
   Bring it back with `docker compose start users-service`.

Stop everything with `docker compose down` (add `-v` to also delete the data).

### Run the tests and style checks

```bash
cd users-service && uv run pytest     # same for orders-service
uvx ruff check .                      # PEP 8 check, from the project root
```

## Learning log

| Week | What I learned | What it added |
|---|---|---|
| 1 | Containers, Docker, uv, FastAPI, microservices | Two services in their own containers, talking over HTTP |
| 2 | SQLite, unit testing, PEP 8 with Ruff | A database per service, 23 tests, code-style checks in CI |
