from datetime import datetime, timezone

from app.extensions import db


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    posts = db.relationship("Post", back_populates="author")

    def to_dict(self):
        return {"id": self.id, "name": self.name, "email": self.email}


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    posts = db.relationship("Post", back_populates="category")

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class Post(db.Model):
    __tablename__ = "posts"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)

    author = db.relationship("Author", back_populates="posts")
    category = db.relationship("Category", back_populates="posts")

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
            "author": self.author.to_dict(),
            "category": self.category.to_dict() if self.category else None,
        }