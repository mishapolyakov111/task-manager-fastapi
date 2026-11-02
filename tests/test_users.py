async def test_create_user(client):
    response = await client.post(
        "/users", json={"email": "alice@example.com", "name": "Alice"}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["email"] == "alice@example.com"
    assert body["name"] == "Alice"


async def test_duplicate_email(client):
    payload = {"email": "alice@example.com", "name": "Alice"}
    await client.post("/users", json=payload)

    response = await client.post("/users", json=payload)

    assert response.status_code == 409


async def test_invalid_email(client):
    response = await client.post(
        "/users", json={"email": "not-an-email", "name": "Alice"}
    )

    assert response.status_code == 422


async def test_process_time_header(client):
    response = await client.get("/users/1")

    assert "X-Process-Time" in response.headers
    assert float(response.headers["X-Process-Time"]) >= 0
