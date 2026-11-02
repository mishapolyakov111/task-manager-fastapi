async def test_create_task(client, user):
    response = await client.post(
        "/tasks", json={"title": "Buy milk", "owner_id": user["id"]}
    )

    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Buy milk"
    assert body["done"] is False
    assert body["owner_id"] == user["id"]


async def test_create_task_unknown_owner(client):
    response = await client.post("/tasks", json={"title": "Buy milk", "owner_id": 999})

    assert response.status_code == 404


async def test_filter_done_and_pagination(client, user):
    for i in range(5):
        await client.post(
            "/tasks",
            json={"title": f"Task {i}", "done": i % 2 == 0, "owner_id": user["id"]},
        )

    done = await client.get("/tasks", params={"done": True})
    first_page = await client.get("/tasks", params={"done": True, "limit": 2})
    second_page = await client.get(
        "/tasks", params={"done": True, "limit": 2, "offset": 2}
    )

    assert [task["title"] for task in done.json()] == ["Task 0", "Task 2", "Task 4"]
    assert [task["title"] for task in first_page.json()] == ["Task 0", "Task 2"]
    assert [task["title"] for task in second_page.json()] == ["Task 4"]


async def test_patch_changes_only_given_fields(client, user):
    created = await client.post(
        "/tasks",
        json={"title": "Buy milk", "description": "2 liters", "owner_id": user["id"]},
    )
    task_id = created.json()["id"]

    response = await client.patch(f"/tasks/{task_id}", json={"done": True})

    assert response.status_code == 200
    body = response.json()
    assert body["done"] is True
    assert body["title"] == "Buy milk"
    assert body["description"] == "2 liters"


async def test_delete_then_get_404(client, user):
    created = await client.post(
        "/tasks", json={"title": "Buy milk", "owner_id": user["id"]}
    )
    task_id = created.json()["id"]

    deleted = await client.delete(f"/tasks/{task_id}")
    response = await client.get(f"/tasks/{task_id}")

    assert deleted.status_code == 204
    assert response.status_code == 404
