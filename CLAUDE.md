# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Quick start

```powershell
.venv\Scripts\Activate.ps1
python manage.py runserver        # http://127.0.0.1:8000
python manage.py test             # 179 tests
python manage.py test hotels      # single app
python manage.py test bookings.tests.BookingCreateViewTests  # single class
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

`python` = Python 3.12 from `.venv`. Use `Activate.ps1` (not `activate`).

## Architecture

Django 6.0.6 hotel booking platform with seven apps under `django_project/settings.py`.

| App | Purpose | Namespace |
|---|---|---|
| `accounts` | Auth: email-based login, CustomUser (+Profile via signal), roles (customer/owner) | `accounts` |
| `pages` | Home page showing up to 6 featured hotels from DB | `pages` |
| `hotels` | Hotel CRUD — create/edit/delete gated to hotel owners | `hotels` |
| `rooms` | Room CRUD per hotel — owner-gated, linked from hotel detail | `rooms` |
| `bookings` | Booking CRUD — user-scoped, auto-computes total_price | `bookings` |
| `payments` | Payment per booking (OneToOne) — auto-sets amount from booking | `payments` |
| `reviews` | Reviews per hotel — one per user per hotel (UniqueConstraint) | `reviews` |

All templates extend `templates/base.html` (inlined CSS with CSS variables, no CSS framework). Forms use `form-control` class on widgets.

### Dependencies

Minimal: Django 6.0.6, Pillow, Whitenoise 6.9, dj-database-url, psycopg2-binary, cloudinary (optional, gated on `CLOUDINARY_URL`). No linter, formatter, type checker, or CI.

### Auth & permissions

- `AUTH_USER_MODEL = "accounts.CustomUser"`, login by email (`USERNAME_FIELD = "email"`), `username` still in `REQUIRED_FIELDS`.
- Role: `customer` (default) or `owner`. Only owners can create/edit/delete hotels and rooms.
- Profile auto-created via `post_save` signal; profile update view has null-safety fallback.
- `EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"` — password reset prints to console.

### Django 6.0 quirks

- **`static()` import**: from `django.conf.urls.static`, not `django.contrib.staticfiles`.
- **`handle_no_permission`**: `AccessMixin` raises `PermissionDenied` for any authenticated user who fails `test_func()`, even without `raise_exception=True`. Override with `messages.error()` + `redirect()`. When combining `LoginRequiredMixin` + `UserPassesTestMixin`, override must check `is_authenticated` first or unauthenticated users won't get the login redirect.
- **`ImageField`**: `.image` attribute returns `ImageFieldFile` wrapper when empty, not Python `None`. Test with `assertFalse` not `assertIsNone`.

## Models

| Model | Key fields | Relationships |
|---|---|---|
| `Hotel` | owner, name, description, city, country, image, is_active, timestamps | FK → CustomUser |
| `Room` | hotel, room_number, room_type (single/double/deluxe/suite/family), price_per_night (Decimal), capacity, total/available_rooms, image, is_available, timestamps | FK → Hotel |
| `Booking` | user, room, check_in, check_out, guests, total_price (auto-computed), status (pending/confirmed/cancelled/completed), timestamps | FK → User, FK → Room |
| `Payment` | booking (OneToOne), amount (auto-set), payment_method (card/paypal/bank/cash), transaction_id, status (pending/completed/failed/refunded), paid_at, timestamps | OneToOne → Booking |
| `Review` | user, hotel, rating (1-5 PositiveSmallInteger), comment, timestamps. UniqueConstraint on (user, hotel) | FK → User, FK → Hotel |

## Key URLs by namespace

**`hotels`**: `/hotels/` (list, paginated 9/page), `/hotels/<id>/` (detail with rooms + reviews inline), `/hotels/create/`, `/hotels/<id>/edit/`, `/hotels/<id>/delete/`

**`rooms`**: `/rooms/` (list, paginated 12/page, available only), `/rooms/<id>/`, `/rooms/create/`, `/rooms/<id>/edit/`, `/rooms/<id>/delete/`

**`bookings`**: `/bookings/` (user-scoped list, paginated 10/page), `/bookings/create/`, `/bookings/<id>/`

**`payments`**: `/payments/create/<booking_id>/` (auto-sets amount from booking.total_price; redirects if payment already exists), `/payments/<id>/`

**`reviews`**: `/reviews/create/<hotel_id>/` (one per user per hotel; duplicate redirects to edit), `/reviews/<id>/edit/`, `/reviews/<id>/delete/`. No ReviewListView/ReviewDetailView — reviews display inline on hotel detail page.

## Known gotchas

- Booking create has no availability validation — `total_price = room.price_per_night * days`.
- Only one payment allowed per booking (redirects if exists).
- `media/` is gitignored; images upload to `media/hotels/`, `media/rooms/`, `media/profiles/`.
- `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS` hardcoded in settings (overridable via env vars).
- Cloudinary optional: activated only if `CLOUDINARY_URL` contains `cloudinary://`.
- Tests use Django's `TestCase` (unittest-based). Each app has its own `tests.py` with setUp creating users/hotels/rooms.

## Deployment

- Hosted on PythonAnywhere (`pythonanywhere_wsgi.py`).
- Environment vars: `DJANGO_SECRET_KEY`, `DJANGO_DEBUG`, `DJANGO_ALLOWED_HOSTS`, `DATABASE_URL`, `CLOUDINARY_URL`.
- Static files served via Whitenoise (CompressedManifestStaticFilesStorage in production).
- Health check at `/health/`, DB debug at `/debug-db/`.
