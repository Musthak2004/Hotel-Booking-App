# AGENTS.md

## Quick start

```powershell
.venv\Scripts\Activate.ps1
python manage.py runserver        # dev server — http://127.0.0.1:8000
python manage.py test             # all 36 tests (~8s)
python manage.py test accounts    # single app (27 tests)
python manage.py test pages       # single app (9 tests)
python manage.py test accounts.tests.CustomUserModelTests.test_create_user_with_email  # single test
python manage.py makemigrations   # after model changes
python manage.py migrate
python manage.py createsuperuser  # username + email + password (username still required)
```

`python` = Python 3.13.5 from `.venv`. Activate venv first (note: `Activate.ps1`, not `activate`).

## Architecture

- **Django 6.0.6**, two apps: `accounts/` (auth) and `pages/` (home page via `TemplateView`).
- Templates live in `templates/` (project-level — **not** inside apps). Django auth templates are in `templates/registration/`.
- CSS is inlined in `<style>` blocks in each template (no external CSS, no staticfiles setup). All templates inherit from `base.html` which defines CSS variables (`--accent`, `--error`, `--success`, `--warning`, `--border`, `--radius`, `--shadow`, etc.) usable in child template `<style>` blocks.
- No linter, formatter, type checker, or CI. Only dependency beyond Django is Pillow (for `profile_picture` ImageField).
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` hardcoded in settings — no env management.

## URLs

Auth URLs are defined **explicitly** in `accounts/urls.py` (not via `django.contrib.auth.urls`) with inline `as_view()` calls:

| URL pattern | View | Template |
|---|---|---|
| `login/` | `LoginView` | `registration/login.html` |
| `logout/` | `LogoutView` | (default) |
| `signup/` | `SignUpView` (custom `CreateView`) | `registration/signup.html` |
| `profile/update/` | `profile_update` (custom, `@login_required`) | `registration/profile_update.html` |
| `password_change/` | `PasswordChangeView` | `registration/password_change_form.html` |
| `password_change/done/` | `PasswordChangeDoneView` | `registration/password_change_done.html` |
| `password_reset/` | `PasswordResetView` | `registration/password_reset_form.html` |
| `password_reset/done/` | `PasswordResetDoneView` | `registration/password_reset_done.html` |
| `reset/<uidb64>/<token>/` | `PasswordResetConfirmView` | `registration/password_reset_confirm.html` |
| `reset/done/` | `PasswordResetCompleteView` | `registration/password_reset_complete.html` |

Project wiring: `django_project/urls.py` includes `accounts.urls` and `pages.urls`. In `DEBUG` mode, it also serves `MEDIA_URL` via `django.conf.urls.static.static`.

## Key gotchas

| Gotcha | Detail |
|---|---|
| **Custom user model** | `AUTH_USER_MODEL = "accounts.CustomUser"`. `USERNAME_FIELD = "email"`, but `username` is still in `REQUIRED_FIELDS`. Login by email. |
| **Signal auto-creates Profile** | `accounts/signals.py` hooks `post_save` on `CustomUser`. Every user created (admin, shell, tests) gets a `Profile`. Connected via `AccountsConfig.ready()` in `apps.py`. |
| **CustomUser fields** | `email` (unique), `phone_number` (blank), `role` (`customer`/`owner`, default `customer`). |
| **Profile fields** | `address`, `city`, `country`, `postal_code` (all blank-able), `profile_picture` (ImageField, `profiles/`). MEDIA_ROOT and MEDIA_URL configured in settings, but uploading may need `media/` directory. |
| **Profile update wired** | `accounts/views.py:15` has a `@login_required` `profile_update` view (handles both `CustomUserUpdateForm` and `ProfileUpdateForm`). URL: `accounts/profile/update/`. Template: `registration/profile_update.html`. |
| **Signup form** | `CustomUserRegistrationForm` extends `UserCreationForm`. Fields: username, email, phone_number, role, password1, password2. Widgets use `form-control` CSS class. |
| **Email backend** | `EMAIL_BACKEND = "django.core.email.backends.console.EmailBackend"` — password reset emails print to console. |
| **static() import** | Import from `django.conf.urls.static`, not `django.contrib.staticfiles` (Django 6.0 changed this). |
| **Nav dropdown convention** | Authenticated users see a clickable user badge (top-right). Opens a dropdown with **Settings** (`password_change`) and **Log out**. Mobile hamburger menu has the same items inline. |
| **`static()` import** | From `django.conf.urls.static`, not `django.contrib.staticfiles` (Django 6.0 change). |
