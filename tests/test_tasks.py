def test_register_and_login(client):
    r = client.post("/auth/register", json={"username": "alice", "password": "hunter2hunter2"})
    assert r.status_code == 201
    assert r.json()["username"] == "alice"

    r = client.post("/auth/register", json={"username": "alice", "password": "hunter2hunter2"})
    assert r.status_code == 400

    r = client.post("/auth/login", data={"username": "alice", "password": "hunter2hunter2"})
    assert r.status_code == 200
    assert "access_token" in r.json()

    r = client.post("/auth/login", data={"username": "alice", "password": "wrong"})
    assert r.status_code == 401


def test_create_and_get_task(auth_client):
    payload = {"title": "write tests", "description": "for the task manager", "due_date": "2026-10-01"}
    r = auth_client.post("/tasks", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["title"] == "write tests"
    assert body["completed"] is False

    r = auth_client.get("/tasks")
    assert r.status_code == 200
    tasks = r.json()
    assert len(tasks) == 1
    assert tasks[0]["id"] == body["id"]


def test_update_task(auth_client):
    created = auth_client.post("/tasks", json={"title": "original"}).json()

    update_payload = {"title": "updated", "description": "now with details", "completed": True}
    r = auth_client.put("/tasks/%d" % created["id"], json=update_payload)
    assert r.status_code == 200
    body = r.json()
    assert body["title"] == "updated"
    assert body["completed"] is True

    r = auth_client.put("/tasks/9999", json={"title": "ghost"})
    assert r.status_code == 404


def test_delete_task(auth_client):
    created = auth_client.post("/tasks", json={"title": "temporary"}).json()

    r = auth_client.delete(f"/tasks/{created['id']}")
    assert r.status_code == 204

    r = auth_client.get("/tasks")
    assert r.json() == []

    r = auth_client.delete("/tasks/%d" % created["id"])
    assert r.status_code == 404


def test_unauthorized_access_returns_401(client):
    assert client.get("/tasks").status_code == 401
    assert client.post("/tasks", json={"title": "nope"}).status_code == 401
    assert client.put("/tasks/1", json={"title": "nope"}).status_code == 401
    assert client.delete("/tasks/1").status_code == 401

    client.headers.update({"Authorization": "Bearer garbage"})
    assert client.get("/tasks").status_code == 401
