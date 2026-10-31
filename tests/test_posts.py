def test_list_posts_is_public(client):
    response = client.get("/posts")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_post_requires_login(client):
    response = client.post("/posts", json={"title": "Hi", "content": "Hello"})
    assert response.status_code == 401


def test_create_post_with_token(client, login):
    headers = login()
    response = client.post(
        "/posts", json={"title": "My post", "content": "Hello!"}, headers=headers
    )
    assert response.status_code == 201
    assert response.get_json()["author"]["name"] == "Neha"


def test_get_missing_post_returns_404(client):
    response = client.get("/posts/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_cannot_edit_someone_elses_post(client, login):
    neha = login()
    post_id = client.post(
        "/posts", json={"title": "Neha's post", "content": "Mine"}, headers=neha
    ).get_json()["id"]

    sam = login(name="Sam", email="sam@example.com", password="samsecret123")
    response = client.put(f"/posts/{post_id}", json={"title": "Hacked"}, headers=sam)
    assert response.status_code == 403


def test_owner_can_delete_post(client, login):
    headers = login()
    post_id = client.post(
        "/posts", json={"title": "Temp", "content": "Delete me"}, headers=headers
    ).get_json()["id"]

    response = client.delete(f"/posts/{post_id}", headers=headers)
    assert response.status_code == 204
    assert client.get(f"/posts/{post_id}").status_code == 404