# AGENTS.md

## Quick start

```powershell
.venv\Scripts\activate
python manage.py runserver        # dev server — http://127.0.0.1:8000
python manage.py test             # all 36 tests (~10s)
python manage.py test accounts    # single app (27 tests)
python manage.py test pages       # single app (9 tests)
python manage.py test accounts.tests.CustomUserModelTests  # single class
python manage.py test accounts.tests.CustomUserModelTests.test_create_user_with_email  # single test
python manage.py makemigrations   # after model changes
python manage.py migrate
python manage.py createsuperuser  # username + email + password (username still required)
```

`python` = Python 3.13.5 from `.venv`. Activate venv first.

## Architecture

- **Django 6.0.6**, two apps: `accounts/` (auth) and `pages/` (home page via `TemplateView`).
- Templates live in `templates/` (project-level — **not** inside apps). Django auth templates are in `templates/registration/`.
- CSS is inlined in `<style>` blocks in each template (no external CSS, no staticfiles setup). All templates inherit from `base.html` which defines CSS variables (`--accent`, `--error`, `--success`, `--warning`, `--border`, `--radius`, `--shadow`, etc.) usable in child template `<style>` blocks.
- No linter, formatter, type checker, CI, or `requirements.txt` yet.

## URLs

Auth URLs are defined **explicitly** in `accounts/urls.py` (not via `django.contrib.auth.urls`) with inline `as_view()` calls:

| URL pattern | View | Template |
|---|---|---|
| `login/` | `LoginView` | `registration/login.html` |
| `logout/` | `LogoutView` | (default) |
| `signup/` | `SignUpView` (custom `CreateView`) | `registration/signup.html` |
| `password_change/` | `PasswordChangeView` | `registration/password_change_form.html` |
| `password_change/done/` | `PasswordChangeDoneView` | `registration/password_change_done.html` |
| `password_reset/` | `PasswordResetView` | `registration/password_reset_form.html` |
| `password_reset/done/` | `PasswordResetDoneView` | `registration/password_reset_done.html` |
| `reset/<uidb64>/<token>/` | `PasswordResetConfirmView` | `registration/password_reset_confirm.html` |
| `reset/done/` | `PasswordResetCompleteView` | `registration/password_reset_complete.html` |

Project wiring: `django_project/urls.py` includes `accounts.urls` and `pages.urls`.

## Key gotchas

| Gotcha | Detail |
|---|---|
| **Custom user model** | `AUTH_USER_MODEL = "accounts.CustomUser"`. `USERNAME_FIELD = "email"`, but `username` is still in `REQUIRED_FIELDS`. Login by email. |
| **Signal auto-creates Profile** | `accounts/signals.py` hooks `post_save` on `CustomUser`. Every user created (admin, shell, tests) gets a `Profile`. Connected via `AccountsConfig.ready()` in `apps.py`. |
| **Profile fields** | `address`, `city`, `country`, `postal_code` (all blank-able), `profile_picture` (ImageField, `profiles/`). No MEDIA_ROOT/MEDIA_URL configured yet — uploading images will fail until set up. |
| **CustomUser fields** | `email` (unique), `phone_number` (blank), `role` (`customer`/`owner`, default `customer`). |
| **Signup form** | `CustomUserRegistrationForm` extends `UserCreationForm`. Fields: username, email, phone_number, role, password1, password2. Widgets use `form-control` CSS class. |
| **Profile forms** | `CustomUserUpdateForm` (username, email, phone_number) and `ProfileUpdateForm` (address, city, country, postal_code, profile_picture) exist but have **no views or templates** yet — not wired to any URL. |
| **Email backend** | `EMAIL_BACKEND = "django.core.email.backends.console.EmailBackend"` — password reset emails print to console. |
| **No .gitignore** | `db.sqlite3`, `__pycache__/`, `.venv/` not excluded. |
| **No requirements.txt** | Dependencies only in `.venv`. Run `pip freeze > requirements.txt` before adding deps. |
| **Nav dropdown convention** | Authenticated users see a clickable user badge (top-right). Opens a dropdown with **Settings** (`password_change`) and **Log out**. Mobile hamburger menu has the same items inline. |
| **No env management** | `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` hardcoded in settings. |
