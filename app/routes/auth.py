from flask import Blueprint, request
from flask_jwt_extended import create_access_token

from app.extensions import db
from app.models import Author

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name = str(data.get("name", "")).strip()
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    if not name or not email or not password:
        return {"error": "'name', 'email' and 'password' are required."}, 400
    if len(password) < 8:
        return {"error": "Password must be at least 8 characters."}, 400

    existing = db.session.execute(db.select(Author).filter_by(email=email)).scalar_one_or_none()
    if existing:
        return {"error": "An author with this email already exists."}, 409

    author = Author(name=name, email=email)
    author.set_password(password)
    db.session.add(author)
    db.session.commit()
    return author.to_dict(), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))

    author = db.session.execute(db.select(Author).filter_by(email=email)).scalar_one_or_none()
    if author is None or not author.check_password(password):
        return {"error": "Invalid email or password."}, 401

    token = create_access_token(identity=str(author.id))
    return {"access_token": token}