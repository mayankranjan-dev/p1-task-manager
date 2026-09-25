# Task Manager

I built this simple task manager to learn FastAPI and JWT auth. It's a small CRUD API: users register, log in, get a JWT, and use it to manage their own list of tasks. Nothing fancier than that.

## Stack

- FastAPI
- SQLAlchemy (SQLite by default)
- PyJWT for tokens, passlib/bcrypt for password hashing
- pytest + httpx for tests

## Quickstart

Clone the repo, then from the project root:

```bash
python -m venv venv
venv\Scripts\activate      # on Windows
source venv/bin/activate   # on macOS/Linux

pip install -r requirements.txt
```

Set a real secret key before running anything beyond local experiments:

```bash
export SECRET_KEY="something-long-and-random"   # macOS/Linux
$env:SECRET_KEY = "something-long-and-random"   # Windows PowerShell
```

If you skip it, `auth.py` falls back to a dev-only default so things still run, but don't use that fallback for anything real.

Run the app:

```bash
uvicorn main:app --reload
```

It'll be up at `http://127.0.0.1:8000`, with interactive docs at `/docs`.

Run the tests:

```bash
pytest
```

## API Endpoints

Auth (`/auth`):

- `POST /auth/register` - create a user (`username`, `password`)
- `POST /auth/login` - form login, returns a bearer JWT

Tasks (`/tasks`, all require `Authorization: Bearer <token>`):

- `GET /tasks` - list the current user's tasks, optional `?completed=true|false` filter
- `POST /tasks` - create a task (`title`, `description`, `due_date`, `completed`)
- `PUT /tasks/{id}` - full replace of a task's fields
- `DELETE /tasks/{id}` - delete a task

Every task route is scoped to the authenticated user's own `owner_id`, so one user can't see or touch another user's tasks. A missing or someone-else's task ID both return a 404, not a 403, to avoid confirming a task exists for another account.

`GET /health` is a plain unauthenticated health check.

## Docker / Railway

Build and run locally:

```bash
docker build -t task-manager .
docker run -p 8000:8000 -e SECRET_KEY=something-long-and-random task-manager
```

`railway.toml` points Railway at the Dockerfile for builds. Set `SECRET_KEY` (and `DATABASE_URL` if you move off SQLite) as environment variables in the Railway project settings, not in the repo.

## Known Limitations

- Uses SQLite by default, which is fine for a personal project or demo but not for heavy concurrent production writes. Swapping to PostgreSQL means changing `DATABASE_URL` and adding a driver like `psycopg2-binary` to requirements.txt.
- SQLite storage is a file inside the container. On Railway (or any container platform) that file doesn't persist across redeploys unless you attach a volume, so plan on Postgres before relying on this in any real deployment.
- No token refresh or revocation. JWTs are valid until they expire; there's no logout or blocklist.
- No rate limiting on login or register, so brute-forcing weak passwords isn't blocked at the API level.
- `PUT /tasks/{id}` is a full replace, not a partial update. Omitted fields reset to their schema defaults rather than staying as-is.
- No pagination on `GET /tasks` yet. Fine for a personal task list, not fine if that list grows into the thousands.
