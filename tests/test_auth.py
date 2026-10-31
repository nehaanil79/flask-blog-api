def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"name": "Neha", "email": "neha@example.com", "password": "supersecret123"},
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["email"] == "neha@example.com"
    assert "password_hash" not in data


def test_register_short_password(client):
    response = client.post(
        "/auth/register",
        json={"name": "Neha", "email": "neha@example.com", "password": "short"},
    )
    assert response.status_code == 400


def test_register_duplicate_email(client):
    body = {"name": "Neha", "email": "neha@example.com", "password": "supersecret123"}
    client.post("/auth/register", json=body)
    response = client.post("/auth/register", json=body)
    assert response.status_code == 409


def test_login_returns_token(client, login):
    headers = login()
    assert headers["Authorization"].startswith("Bearer ")


def test_login_wrong_password(client, login):
    login()
    response = client.post(
        "/auth/login", json={"email": "neha@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401