from flask import Blueprint, request

from app.extensions import db
from app.models import Author

authors_bp = Blueprint("authors", __name__, url_prefix="/authors")


@authors_bp.get("")
def list_authors():
    authors = db.session.execute(db.select(Author).order_by(Author.id)).scalars().all()
    return [author.to_dict() for author in authors]


@authors_bp.post("")
def create_author():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()

    if not name or not email:
        return {"error": "Both 'name' and 'email' are required."}, 400

    existing = db.session.execute(db.select(Author).filter_by(email=email)).scalar_one_or_none()
    if existing:
        return {"error": "An author with this email already exists."}, 409

    author = Author(name=name, email=email)
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201