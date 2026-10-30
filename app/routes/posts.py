from flask import Blueprint, request, abort

from app.extensions import db
from app.models import Author, Category, Post

from flask_jwt_extended import get_jwt_identity, jwt_required

posts_bp = Blueprint("posts", __name__, url_prefix="/posts")


@posts_bp.get("")
def list_posts():
    posts = db.session.execute(db.select(Post).order_by(Post.created_at.desc())).scalars().all()
    return [post.to_dict() for post in posts]


@posts_bp.post("")
@jwt_required()
def create_post():
    author = db.session.get(Author, int(get_jwt_identity()))
    if author is None:
        return {"error": "Your account no longer exists. Please log in again."}, 401

    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    content = str(data.get("content", "")).strip()
    category_id = data.get("category_id")

    if not title or not content:
        return {"error": "'title' and 'content' are required."}, 400

    if category_id is not None:
        if not isinstance(category_id, int) or db.session.get(Category, category_id) is None:
            return {"error": f"No category found with id {category_id}."}, 400

    post = Post(title=title, content=content, author=author, category_id=category_id)
    db.session.add(post)
    db.session.commit()
    return post.to_dict(), 201

def get_post_or_404(post_id):
    post = db.session.get(Post, post_id)
    if post is None:
        abort(404, description=f"No post found with id {post_id}.")
    return post

def get_own_post_or_403(post_id):
    post = get_post_or_404(post_id)
    if post.author_id != int(get_jwt_identity()):
        abort(403, description="You can only change your own posts.")
    return post


@posts_bp.get("/<int:post_id>")
def get_post(post_id):
    return get_post_or_404(post_id).to_dict()


@posts_bp.put("/<int:post_id>")
@jwt_required()
def update_post(post_id):
    post = get_own_post_or_403(post_id)
    data = request.get_json(silent=True) or {}

    if not any(field in data for field in ("title", "content", "category_id")):
        return {"error": "Send at least one of 'title', 'content' or 'category_id'."}, 400

    if "title" in data:
        title = str(data["title"]).strip()
        if not title:
            return {"error": "'title' cannot be empty."}, 400
        post.title = title

    if "content" in data:
        content = str(data["content"]).strip()
        if not content:
            return {"error": "'content' cannot be empty."}, 400
        post.content = content

    if "category_id" in data:
        category_id = data["category_id"]
        if category_id is not None:
            if not isinstance(category_id, int) or db.session.get(Category, category_id) is None:
                return {"error": f"No category found with id {category_id}."}, 400
        post.category_id = category_id

    db.session.commit()
    return post.to_dict()


@posts_bp.delete("/<int:post_id>")
@jwt_required()
def delete_post(post_id):
    post = get_own_post_or_403(post_id)
    db.session.delete(post)
    db.session.commit()
    return "", 204