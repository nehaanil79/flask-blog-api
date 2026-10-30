from flask import Flask

from app.extensions import db, jwt
from config import Config

from app import models  # noqa: F401

from app.routes.authors import authors_bp
from app.routes.posts import posts_bp
from app.routes.categories import categories_bp
from app.routes.auth import auth_bp

from werkzeug.exceptions import HTTPException

from flask_cors import CORS


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    jwt.init_app(app)
    CORS(app)

    app.register_blueprint(authors_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(auth_bp)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return {"error": error.description}, error.code

    @jwt.unauthorized_loader
    def missing_token(reason):
        return {"error": "Login required. Send a valid token in the Authorization header."}, 401

    @jwt.invalid_token_loader
    def invalid_token(reason):
        return {"error": "Invalid token. Please log in again."}, 401

    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return {"error": "Your session has expired. Please log in again."}, 401

    return app