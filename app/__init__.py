from flask import Flask

from app.extensions import db
from config import Config

from app import models  # noqa: F401

from app.routes.authors import authors_bp
from app.routes.posts import posts_bp
from app.routes.categories import categories_bp

from werkzeug.exceptions import HTTPException


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    app.register_blueprint(authors_bp)
    app.register_blueprint(posts_bp)
    app.register_blueprint(categories_bp)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.errorhandler(HTTPException)
    def handle_http_error(error):
        return {"error": error.description}, error.code

    return app