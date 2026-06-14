# AGENTS.md

## Quick start

```powershell
.venv\Scripts\Activate.ps1
python manage.py runserver        # http://127.0.0.1:8000
python manage.py test             # 130 tests
python manage.py test hotels      # single app
python manage.py test bookings.tests.BookingCreateViewTests  # single class
python manage.py makemigrations   # after model changes
python manage.py migrate
python manage.py createsuperuser  # username + email + password
```

`python` = Python 3.13.5 from `.venv`. Use `Activate.ps1` (not `activate`).

## Architecture

Five Django apps under `django_project/settings.py`. Namespaces: `hotels`, `rooms`, `bookings`.

| App | Role | Templates |
|---|---|---|
| `accounts` | Auth (custom user, signup, profile) | `templates/registration/` (project-level) |
| `pages` | Home page (featured hotels from DB) | `templates/home.html` |
| `hotels` | Hotel CRUD, owner-gated | `hotels/templates/hotels/` |
| `rooms` | Room CRUD per hotel, owner-gated | `rooms/templates/rooms/` |
| `bookings` | Booking CRUD per user | `bookings/templates/bookings/` |

All templates extend `templates/base.html` (inlined CSS with CSS variables, `form-control` class on widgets).

## Auth

- `AUTH_USER_MODEL = "accounts.CustomUser"`, login by email (`USERNAME_FIELD = "email"`), `username` still in `REQUIRED_FIELDS`.
- Role: `customer` (default) or `owner`. Only owners can create/edit/delete hotels and rooms.
- Profile auto-created via `post_save` signal; profile update view has null-safety fallback.
- `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"` — password reset prints to console.

## Django 6.0 quirks

- **`static()` import**: from `django.conf.urls.static`, not `django.contrib.staticfiles`.
- **`handle_no_permission`**: `AccessMixin` raises `PermissionDenied` for any authenticated user who fails `test_func()`, even without `raise_exception=True`. Override with `messages.error()` + `redirect()`. When combining `LoginRequiredMixin` + `UserPassesTestMixin`, override must check `is_authenticated` first or unauthenticated users won't get the login redirect.
- **`ImageField`**: `.image` attribute returns `ImageFieldFile` wrapper when empty, not Python `None`. Test with `assertFalse` not `assertIsNone`.

## Models

- `Hotel`: `owner` (FK CustomUser), `name`, `description`, `address`, `city`, `country`, `phone_number` (blank), `email` (blank), `image` (nullable), `is_active`, `created_at`, `updated_at`. No rating/lat/lng.
- `Room`: `hotel` (FK Hotel), `room_number`, `room_type` (single/double/deluxe/suite/family), `description` (blank), `price_per_night` (Decimal), `capacity` (default 1), `total_rooms` (default 1), `available_rooms` (default 1), `image` (nullable), `is_available`, `created_at`, `updated_at`.
- `Booking`: `user` (FK CustomUser), `room` (FK Room), `check_in`, `check_out`, `guests` (default 1), `total_price` (Decimal, auto-computed on create), `status` (pending/confirmed/cancelled/completed), `created_at`, `updated_at`.

## Gotchas

- Only dependency beyond Django is Pillow. No linter, formatter, type checker, or CI.
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` hardcoded in settings.
- `media/` is gitignored; images upload to `media/hotels/`, `media/rooms/`, `media/profiles/`.
- Booking create has no availability validation — `total_price = room.price_per_night * days`.
