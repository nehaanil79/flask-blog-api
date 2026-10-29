from flask import Blueprint, request

from app.extensions import db
from app.models import Author

authors_bp = Blueprint("authors", __name__, url_prefix="/authors")


@authors_bp.get("")
def list_authors():
    authors = db.session.execute(db.select(Author).order_by(Author.id)).scalars().all()
    return [author.to_dict() for author in authors]
