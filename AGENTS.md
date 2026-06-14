# AGENTS.md

## Quick start

```powershell
.venv\Scripts\Activate.ps1
python manage.py runserver        # dev server — http://127.0.0.1:8000
python manage.py test             # all tests
python manage.py test accounts    # accounts app tests
python manage.py test pages       # pages app tests
python manage.py test hotels      # hotels app tests
python manage.py test accounts.tests.CustomUserModelTests.test_create_user_with_email  # single test
python manage.py makemigrations   # after model changes
python manage.py migrate
python manage.py createsuperuser  # username + email + password (username still required)
```

`python` = Python 3.13.5 from `.venv`. Activate venv first (note: `Activate.ps1`, not `activate`).

## Apps

Three apps: `accounts/` (auth), `pages/` (home page), `hotels/` (hotel listing).

| App | Templates | Entrypoints |
|---|---|---|
| `accounts` | `templates/registration/` (project-level) | `accounts/urls.py`, `accounts/views.py`, `accounts/models.py`, `accounts/forms.py`, `accounts/signals.py` |
| `pages` | `templates/home.html` (project-level) | `pages/urls.py`, `pages/views.py` |
| `hotels` | `hotels/templates/hotels/` (app-level) | `hotels/urls.py` (namespace `hotels`), `hotels/views.py`, `hotels/models.py`, `hotels/admin.py` |

Accounts and pages templates live in project-level `templates/`. Hotels templates live inside the app. All inherit from `base.html`. CSS is inlined in `<style>` blocks using CSS variables (`--accent`, `--error`, `--success`, `--warning`, `--border`, `--radius`, `--shadow`, etc.).

## Auth URLs (defined explicitly in `accounts/urls.py`)

| URL pattern | View name | Template |
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

Project wiring: `django_project/urls.py` includes `accounts.urls`, `pages.urls`, and `hotels.urls`. In `DEBUG` mode, serves `MEDIA_URL` via `django.conf.urls.static.static`.

## Hotels app

- URL: `/hotels/`, namespace `hotels`, view name `hotel_list`
- `HotelListView` at `hotels/views.py` — filtered by `q` (name), `city`, `sort` (rating/name) query params. Paginates 9 per page. Provides `cities` context via `get_context_data()`.
- `Hotel` model at `hotels/models.py`: `owner` (FK CustomUser), `name`, `description`, `address`, `city`, `country`, `phone_number`, `email`, `rating` (Decimal, 0.0–5.0), `image`, `latitude`, `longitude`, `is_active`, `created_at`, `updated_at`.
- Admin registered at `hotels/admin.py` with list display, filters, search, and fieldsets.

## Key gotchas

| Gotcha | Detail |
|---|---|
| **Custom user model** | `AUTH_USER_MODEL = "accounts.CustomUser"`. `USERNAME_FIELD = "email"`, but `username` is still in `REQUIRED_FIELDS`. Login by email. |
| **Signal auto-creates Profile** | `accounts/signals.py` hooks `post_save` on `CustomUser`. Every user created (admin, shell, tests) gets a `Profile`. Connected via `AccountsConfig.ready()` in `apps.py`. |
| **CustomUser fields** | `email` (unique), `phone_number` (blank), `role` (`customer`/`owner`, default `customer`). |
| **Profile fields** | `address`, `city`, `country`, `postal_code` (all blank-able), `profile_picture` (ImageField, `profiles/`). MEDIA_ROOT and MEDIA_URL configured, but uploading may need `media/` directory. |
| **Profile update view** | `accounts/views.py:14` — `@login_required` function view handling both `CustomUserUpdateForm` and `ProfileUpdateForm`. URL: `accounts/profile/update/`. Template: `registration/profile_update.html`. |
| **Signup form** | `CustomUserRegistrationForm` extends `UserCreationForm`. Fields: username, email, phone_number, role, password1, password2. Widgets use `form-control` CSS class. |
| **Email backend** | `EMAIL_BACKEND = "django.core.email.backends.console.EmailBackend"` — password reset emails print to console. |
| **`static()` import** | From `django.conf.urls.static`, not `django.contrib.staticfiles` (Django 6.0 change). |
| **Nav dropdown** | Authenticated users see a clickable user badge (top-right). Opens a dropdown with **Profile Update** (`profile_update`), **Settings** (`password_change`), and **Log out**. Mobile hamburger menu has the same items inline. |
| **Mobile menu Booking** | Desktop nav links to `hotels:hotel_list`; mobile menu still uses `#` as placeholder. |
| **No linter/CI** | No linter, formatter, type checker, or CI. Only dependency beyond Django is Pillow. `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` hardcoded. `TIME_ZONE = "America/New_York"`. |
| **Django 6.0** | Template setting uses `DIRS: [BASE_DIR / 'templates']`. `static()` import from `django.conf.urls.static`. |
