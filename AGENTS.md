# AGENTS.md

## Quick start

```powershell
.venv\Scripts\Activate.ps1
python manage.py runserver        # dev server — http://127.0.0.1:8000
python manage.py test             # all 36 tests
python manage.py test accounts    # accounts app tests
python manage.py test pages       # pages app tests
python manage.py test hotels      # hotels app tests
python manage.py test accounts.tests.CustomUserModelTests.test_create_user_with_email  # single test
python manage.py makemigrations   # after model changes
python manage.py migrate
python manage.py createsuperuser  # username + email + password required
```

`python` = Python 3.13.5 from `.venv`. Use `Activate.ps1` (not `activate`).

## Architecture

Three Django apps under `django_project/` settings:

| App | Role | Templates | Entrypoints |
|---|---|---|---|
| `accounts` | Auth (custom user, signup, profile) | `templates/registration/` (project-level) | `urls.py`, `views.py`, `models.py`, `forms.py`, `signals.py` |
| `pages` | Home page | `templates/home.html` (project-level) | `urls.py`, `views.py` |
| `hotels` | Hotel CRUD | `hotels/templates/hotels/` (app-level) | `urls.py` (namespace `hotels`), `views.py`, `models.py`, `admin.py`, `forms.py` |

Project-level `templates/base.html` has inlined CSS with CSS variables (`--accent`, `--error`, `--success`, `--border`, `--radius`, `--shadow`, etc.). All templates inherit from it.

## Hotels app

- **Views** (`hotels/views.py`): `HotelListView`, `HotelDetailView`, `HotelCreateView`, `HotelUpdateView`, `HotelDeleteView`
- **URLs** (`hotels/urls.py`, namespace `hotels`):

| URL | View name | Template |
|---|---|---|
| `/hotels/` | `hotel_list` | `hotel_list.html` |
| `/hotels/<pk>/` | `hotel_detail` | `hotel_detail.html` |
| `/hotels/create/` | `hotel_create` | `hotel_form.html` |
| `/hotels/<pk>/edit/` | `hotel_update` | `hotel_form.html` |
| `/hotels/<pk>/delete/` | `hotel_delete` | `hotel_confirm_delete.html` |

- **Filtering**: `?q=` (name icontains), `?city=` (iexact), `?sort=name` (default: newest first). Paginates 9 per page. Provides `cities` and `current_*` context.
- **Home page** (`pages/views.py`): passes `featured_hotels` (6 most recent active) to template.

## Auth URLs (`accounts/urls.py`, prefix `/accounts/`)

| URL | View name | Template |
|---|---|---|
| `login/` | `login` | `registration/login.html` |
| `logout/` | `logout` | (default) |
| `signup/` | `signup` | `registration/signup.html` |
| `profile/update/` | `profile_update` | `registration/profile_update.html` |
| `password_change/` | `password_change` | `registration/password_change_form.html` |
| `password_change/done/` | `password_change_done` | `registration/password_change_done.html` |
| `password_reset/` | `password_reset` | `registration/password_reset_form.html` |
| `password_reset/done/` | `password_reset_done` | `registration/password_reset_done.html` |
| `reset/<uidb64>/<token>/` | `password_reset_confirm` | `registration/password_reset_confirm.html` |
| `reset/done/` | `password_reset_complete` | `registration/password_reset_complete.html` |

## Key gotchas

| Gotcha | Detail |
|---|---|
| **Custom user model** | `AUTH_USER_MODEL = "accounts.CustomUser"`. `USERNAME_FIELD = "email"` — login by email, but `username` is still in `REQUIRED_FIELDS`. |
| **Role system** | `role` field: `customer` (default) or `owner`. Only `owner` users can create/edit/delete hotels — gated by `UserPassesTestMixin`. |
| **Django 6.0 403 quirk** | `AccessMixin.handle_no_permission` raises `PermissionDenied` for **any authenticated user** who fails a test (not just when `raise_exception=True`). Views override it with `messages.error()` + `redirect()`. Messages CSS is in `base.html`. |
| **Signal auto-creates Profile** | `accounts/signals.py` — only `create_user_profile` on `post_save` (the old `save_user_profile` was removed). Connected via `AccountsConfig.ready()`. Profile update view has null-safety fallback. |
| **Profile update view** | `accounts/views.py` — `@login_required` function view handling both `CustomUserUpdateForm` and `ProfileUpdateForm`. URL: `accounts/profile/update/`. |
| **Email backend** | `django.core.mail.backends.console.EmailBackend` — password reset emails print to console. |
| **`static()` import** | From `django.conf.urls.static`, not `django.contrib.staticfiles` (Django 6.0 change). |
| **No linter/CI** | No linter, formatter, type checker, or CI. Only dependency beyond Django is Pillow. `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` hardcoded. |
| **Hotel model fields** | `owner` (FK CustomUser), `name`, `description`, `address`, `city`, `country`, `phone_number` (blank), `email` (blank), `image` (nullable), `is_active`, `created_at`, `updated_at`. No `rating`/`latitude`/`longitude` — those were removed. |
| **Image uploads** | Hotel images → `media/hotels/`. Profile pictures → `media/profiles/`. `media/` directory is gitignored. |
| **CSS convention** | All CSS is inlined in `<style>` blocks using CSS custom properties defined in `base.html`. No external stylesheets. Form fields use `form-control` class. |
