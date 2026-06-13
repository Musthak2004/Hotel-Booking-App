# AGENTS.md

## Quick start

```powershell
.venv\Scripts\activate
python manage.py runserver        # dev server
python manage.py test             # all tests
python manage.py test accounts    # single app
python manage.py test accounts.tests.TestClass.test_method  # single test
python manage.py makemigrations   # after model changes
python manage.py migrate
```

`python` = Python 3.13.5 from `.venv`. Activate venv first.

## Architecture

- **Django 6.0.6** project, single app (`accounts/`). No monorepo.
- `django_project/settings.py` — all config. No env vars; `SECRET_KEY` and `DEBUG` are hardcoded.
- SQLite (`db.sqlite3`). In-memory SQLite for tests.
- Templates live in `templates/` (project-level), **not** inside apps.
- CSS is inlined in `<style>` blocks — no external CSS or static file setup yet.
- No linter, formatter, type checker, CI, or `requirements.txt` is configured yet.

## Key gotchas

| Gotcha | Detail |
|---|---|
| **Custom user model** | `AUTH_USER_MODEL = "accounts.CustomUser"`. `USERNAME_FIELD = "email"`, but `username` is still in `REQUIRED_FIELDS`. Login is by email. |
| **Signal auto-creates Profile** | `accounts/signals.py` hooks `post_save` on `CustomUser` → every user created (admin, shell, tests) gets a `Profile`. Factor this into test setup. |
| **No `.gitignore` at root** | `db.sqlite3`, `__pycache__/`, `.venv/` are **not** excluded from git. |
| **No `requirements.txt`** | Dependencies only tracked in `.venv`. Run `pip freeze > requirements.txt` before adding deps. |
| **27 tests in `accounts/tests.py`** | Models, forms, views, signals, URLs. `python manage.py test accounts` — 8s. No test config. |
| **No env management** | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, `DATABASE_URL` are all hardcoded. Add `python-decouple` or `django-environ` before going further. |
