# Flask Blog API

**Live API:** https://flask-blog-api-dgdb.onrender.com (health check: [`/health`](https://flask-blog-api-dgdb.onrender.com/health))

A RESTful blog API built with Flask, SQLAlchemy and PostgreSQL. Authors register and log in with JWT authentication, create and manage their own posts, organise posts into categories, and can ask an LLM to suggest tags for a post.

> Hosted on Render's free tier, so the first request after a period of inactivity can take up to a minute while the server wakes up.

## Features

- **Full CRUD for posts**, with partial updates (only the fields you send are changed)
- **Authors and categories**, linked to posts with one-to-many relationships
- **JWT authentication**: register, log in, and send a Bearer token to protected routes
- **Ownership rules**: authors can only update or delete their own posts (403 otherwise)
- **AI tag suggestions**: an LLM (GPT OSS 20B via Groq) suggests 3 to 5 tags for a post
- **Consistent JSON errors** for every failure, e.g. `{"error": "Post not found."}`
- **CORS enabled** so browser front ends on other origins can call the API
- **17 automated tests** with pytest, including mocked AI calls

## Tech stack

Python 3.12, Flask, Flask-SQLAlchemy, PostgreSQL (Neon) with psycopg, SQLite for local development and tests, Flask-JWT-Extended, Werkzeug password hashing (scrypt), Flask-CORS, Groq API (GPT OSS 20B), pytest, Gunicorn, Render, Postman

## Endpoints

| Method | Path | Login needed | Description |
|---|---|---|---|
| GET | `/health` | No | Check the API is running |
| POST | `/auth/register` | No | Create an author account |
| POST | `/auth/login` | No | Log in and receive an access token |
| GET | `/authors` | No | List all authors |
| GET | `/posts` | No | List all posts, newest first |
| GET | `/posts/<id>` | No | Get one post |
| POST | `/posts` | Yes | Create a post (the author comes from the token) |
| PUT | `/posts/<id>` | Yes (owner) | Update a post's title, content or category |
| DELETE | `/posts/<id>` | Yes (owner) | Delete a post |
| POST | `/posts/suggest-tags` | Yes | Suggest tags for a title and content using an LLM |
| GET | `/categories` | No | List all categories, alphabetically |
| POST | `/categories` | Yes | Create a category (names are unique, case-insensitive) |
| GET | `/categories/<id>` | No | Get one category |
| GET | `/categories/<id>/posts` | No | List the posts in a category |

## Authentication

1. Register with `POST /auth/register`:
   ```json
   {"name": "Neha", "email": "neha@example.com", "password": "supersecret123"}
   ```
2. Log in with `POST /auth/login` using the same email and password. The response contains a token:
   ```json
   {"access_token": "eyJhbGciOi..."}
   ```
3. Send the token on protected routes in the `Authorization` header:
   ```
   Authorization: Bearer eyJhbGciOi...
   ```

Tokens expire after 1 hour. Passwords are never stored or returned: only a salted scrypt hash is saved.

## Example: create a post

**Request:** `POST /posts` with a Bearer token

```json
{
  "title": "Getting started with Flask",
  "content": "Flask is a lightweight Python framework for building APIs.",
  "category_id": 1
}
```

**Response:** `201 Created`

```json
{
  "id": 1,
  "title": "Getting started with Flask",
  "content": "Flask is a lightweight Python framework for building APIs.",
  "created_at": "2026-11-03T08:30:00",
  "author": {"id": 1, "name": "Neha", "email": "neha@example.com"},
  "category": {"id": 1, "name": "Machine Learning"}
}
```

## Example: AI tag suggestions

**Request:** `POST /posts/suggest-tags` with a Bearer token

```json
{
  "title": "Getting started with Flask",
  "content": "Flask is a lightweight Python framework for building REST APIs. In this post I set up routes, connect a PostgreSQL database with SQLAlchemy and add JWT login."
}
```

**Response:** `200 OK`

```json
{"tags": ["flask", "python", "rest api", "sqlalchemy", "jwt"]}
```

How it works:

```
title + content
  -> app/ai.py     GPT OSS 20B via Groq, JSON mode, temperature 0, low reasoning effort
  -> clean_tags()  strings only, trimmed, lowercase, "#" removed, max 30 characters,
                   no duplicates, max 5 tags
  -> {"tags": [...]}
```

If the AI service is not configured, unreachable or returns nothing usable, the API returns `503 Service Unavailable` with a clear message instead of crashing.

## Status codes

| Code | Meaning in this API |
|---|---|
| 200 | Success |
| 201 | Created (register, new post, new category) |
| 204 | Deleted, no content returned |
| 400 | Missing or invalid fields (e.g. no title, password under 8 characters) |
| 401 | Missing, invalid or expired token, or wrong email or password |
| 403 | Logged in, but trying to change someone else's post |
| 404 | The post, category or route does not exist |
| 409 | Duplicate email or category name |
| 503 | The AI service is unavailable |

## Key decisions

- **Application factory and blueprints.** `create_app()` builds the app, and each resource (auth, authors, posts, categories) has its own blueprint. This keeps the code organised and lets the tests create a fresh app with a test configuration.
- **The author comes from the token, not the request body.** Nobody can create a post as someone else.
- **Order of checks: 401, then 404, then 403.** First "who are you?", then "does the post exist?", then "is it yours?".
- **The same login error for a wrong email or a wrong password.** Attackers can't use the login form to find out which emails are registered.
- **Secrets live in environment variables.** The JWT secret, database URL and Groq key are in `.env` locally and in Render's Environment settings, never in the code or on GitHub.
- **Compute and storage are separate.** Render's disk is temporary (every deploy or restart starts a fresh container), so the data lives in a managed PostgreSQL database on Neon.
- **Never trust raw LLM output.** JSON mode guarantees valid JSON, and a validation layer guarantees the right shape before anything is returned.
- **The AI route requires a login,** so strangers can't use up the Groq quota.

## Project structure

```
flask-blog-api/
├── app/
│   ├── __init__.py       create_app(), JWT error handlers, JSON error handler, /health
│   ├── extensions.py     db and jwt objects
│   ├── models.py         Author, Category, Post
│   ├── ai.py             suggest_tags() and clean_tags()
│   └── routes/
│       ├── auth.py
│       ├── authors.py
│       ├── categories.py
│       └── posts.py
├── tests/
│   ├── conftest.py       test config (in-memory SQLite) and fixtures
│   ├── test_auth.py
│   ├── test_posts.py
│   └── test_ai.py
├── config.py
├── run.py
├── requirements.txt
├── pytest.ini
└── .python-version
```

## Run it locally

```bash
git clone https://github.com/nehaanil79/flask-blog-api.git
cd flask-blog-api
python -m venv venv
venv\Scripts\activate        # Windows (on macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
```

Create a `.env` file in the project folder:

```
JWT_SECRET_KEY=any-long-random-string
GROQ_API_KEY=gsk_your_key_here
DATABASE_URL=postgresql://user:password@host/dbname
```

`DATABASE_URL` is optional. Without it, the API uses a local SQLite file (`instance/blog.db`). `GROQ_API_KEY` is only needed for the tag suggestion endpoint; you can get a free key at console.groq.com.

Then run:

```bash
python run.py
```

The API runs at `http://127.0.0.1:5000`. Try `http://127.0.0.1:5000/health`.

## Run the tests

```bash
pytest -v
```

The 17 tests use an in-memory SQLite database, so they never touch real data. The AI tests replace the Groq call with a fake using pytest's `monkeypatch`, so they run in seconds without internet access or an API key.

| File | What it covers |
|---|---|
| `test_auth.py` (5) | Register, short password, duplicate email, login returns a token, wrong password |
| `test_posts.py` (6) | Public list, login required, create with a token, missing post 404, editing someone else's post 403, owner can delete |
| `test_ai.py` (6) | Tags returned, login required, missing content 400, AI down 503, tag cleaning, non-list output rejected |

## Deployment

Deployed on Render as a web service connected to this GitHub repo:

- **Build command:** `pip install -r requirements.txt`
- **Start command:** `gunicorn run:app`
- **Environment variables:** `JWT_SECRET_KEY`, `DATABASE_URL` (Neon PostgreSQL) and `GROQ_API_KEY`

Every push to `main` redeploys the API automatically.

## Limitations

- Free-tier hosting, so there's a cold start after inactivity.
- Tables are created with `db.create_all()`, which doesn't change existing tables. A real project would use migrations (e.g. Flask-Migrate).
- Lists aren't paginated, so `GET /posts` returns every post.
- Suggested tags are returned but not saved to the post.
- CORS currently allows all origins. In a real deployment it would be limited to the front end's domain.

## Future improvements

- Save tags to posts (a many-to-many Tag model) and filter posts by tag
- Pagination and search for posts
- Database migrations with Flask-Migrate
- Refresh tokens and rate limiting on login and the AI endpoint
- A React front end that uses this API
