from app.ai import AIServiceError, clean_tags


def test_suggest_tags_returns_tags(client, login, monkeypatch):
    def fake_suggest_tags(title, content):
        return ["flask", "python"]

    monkeypatch.setattr("app.routes.posts.suggest_tags", fake_suggest_tags)
    headers = login()

    response = client.post(
        "/posts/suggest-tags",
        json={"title": "Flask intro", "content": "All about Flask."},
        headers=headers,
    )

    assert response.status_code == 200
    assert response.get_json() == {"tags": ["flask", "python"]}


def test_suggest_tags_requires_login(client):
    response = client.post(
        "/posts/suggest-tags",
        json={"title": "Flask intro", "content": "All about Flask."},
    )

    assert response.status_code == 401


def test_suggest_tags_missing_content_returns_400(client, login):
    headers = login()

    response = client.post(
        "/posts/suggest-tags",
        json={"title": "Flask intro"},
        headers=headers,
    )

    assert response.status_code == 400


def test_suggest_tags_ai_down_returns_503(client, login, monkeypatch):
    def broken_suggest_tags(title, content):
        raise AIServiceError("AI service is unavailable. Please try again later.")

    monkeypatch.setattr("app.routes.posts.suggest_tags", broken_suggest_tags)
    headers = login()

    response = client.post(
        "/posts/suggest-tags",
        json={"title": "Flask intro", "content": "All about Flask."},
        headers=headers,
    )

    assert response.status_code == 503
    assert "error" in response.get_json()


def test_clean_tags_tidies_model_output():
    raw = ["  #Flask ", "python", "PYTHON", 42, "", "rest api", "jwt", "sql", "extra"]

    assert clean_tags(raw) == ["flask", "python", "rest api", "jwt", "sql"]


def test_clean_tags_rejects_non_list():
    assert clean_tags("flask, python") == []