import pytest

from app import create_app
from app.extensions import db
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SQLALCHEMY_ENGINE_OPTIONS = {}
    JWT_SECRET_KEY = "test-secret-key-for-pytest-only-1234567890"


@pytest.fixture
def app():
    app = create_app(TestConfig)
    yield app
    with app.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login(client):
    def _login(name="Neha", email="neha@example.com", password="supersecret123"):
        client.post("/auth/register", json={"name": name, "email": email, "password": password})
        response = client.post("/auth/login", json={"email": email, "password": password})
        token = response.get_json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _login