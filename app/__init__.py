from flask import Flask

from app.extensions import db
from config import Config


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from app import models  # noqa: F401
    from app.routes.authors import authors_bp
    from app.routes.posts import posts_bp

    app.register_blueprint(authors_bp)
    app.register_blueprint(posts_bp)

    with app.app_context():
        db.create_all()

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app