from flask import Blueprint, request

from app.extensions import db
from app.models import Author, Category, Post

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


@posts_bp.get("")
def list_posts():
    posts = db.session.execute(db.select(Post).order_by(Post.created_at.desc())).scalars().all()
    return [post.to_dict() for post in posts]


@posts_bp.post("")
def create_post():
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()
    author_id = data.get("author_id")
    category_id = data.get("category_id")

    if not title or not content or author_id is None:
        return {"error": "'title', 'content' and 'author_id' are required."}, 400

    if not isinstance(author_id, int):
        return {"error": "'author_id' must be a number."}, 400

    author = db.session.get(Author, author_id)
    if author is None:
        return {"error": f"No author found with id {author_id}."}, 400

    if category_id is not None and db.session.get(Category, category_id) is None:
        return {"error": f"No category found with id {category_id}."}, 400

    post = Post(title=title, content=content, author=author, category_id=category_id)
    db.session.add(post)
    db.session.commit()
    return post.to_dict(), 201