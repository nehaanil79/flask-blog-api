from flask import Blueprint, abort, request

from app.extensions import db
from app.models import Category

categories_bp = Blueprint("categories", __name__, url_prefix="/categories")


def get_category_or_404(category_id):
    category = db.session.get(Category, category_id)
    if category is None:
        abort(404, description=f"No category found with id {category_id}.")
    return category


@categories_bp.get("")
def list_categories():
    categories = db.session.execute(db.select(Category).order_by(Category.name)).scalars().all()
    return [category.to_dict() for category in categories]


@categories_bp.post("")
def create_category():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()

    if not name:
        return {"error": "'name' is required."}, 400

    existing = db.session.execute(
        db.select(Category).where(db.func.lower(Category.name) == name.lower())
    ).scalar_one_or_none()
    if existing:
        return {"error": f"A category called '{existing.name}' already exists."}, 409

    category = Category(name=name)
    db.session.add(category)
    db.session.commit()
    return category.to_dict(), 201


@categories_bp.get("/<int:category_id>")
def get_category(category_id):
    return get_category_or_404(category_id).to_dict()


@categories_bp.get("/<int:category_id>/posts")
def list_category_posts(category_id):
    category = get_category_or_404(category_id)
    return [post.to_dict() for post in category.posts]