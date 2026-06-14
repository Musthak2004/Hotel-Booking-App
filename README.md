# Hotel Booking App

A Django 6.0 hotel booking platform with role-based access (customers / hotel owners).

## Tech Stack

- **Python 3.13.5** / **Django 6.0.6** / **SQLite**
- **Pillow** — image uploads
- Console email backend (password reset prints to terminal)

## Features

- **Auth**: email-based login, signup, password change/reset, roles (`customer` / `owner`)
- **Profile**: auto-created via signal, update at `/accounts/profile/update/`
- **Hotels**: browse/search/filter, owner-only CRUD, paginated grid (9/page)
- **Rooms**: browse/search/filter by type, owner-only CRUD, paginated grid (12/page), linked from hotel detail
- **Bookings**: user-scoped CRUD, auto-computed `total_price = price_per_night * nights`, status badges, paginated (10/page)

## Project Structure

```
hotel_booking/
├── accounts/              # Auth (custom user, profile, signals)
├── hotels/                # Hotel CRUD
├── rooms/                 # Room CRUD
├── bookings/              # Booking CRUD
├── pages/                 # Home page
├── templates/             # base.html, home.html, registration/
│   └── registration/      # Login, signup, password reset templates
├── django_project/        # Settings, root URL config
├── media/                 # User uploads (gitignored)
└── manage.py
```

## Quick Start

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser  # username + email + password
python manage.py runserver
```

Visit **http://127.0.0.1:8000**.

## Commands

| Command | Description |
|---|---|
| `python manage.py runserver` | Dev server |
| `python manage.py test` | All 130 tests |
| `python manage.py test hotels` | Single app |
| `python manage.py test bookings.tests.BookingCreateViewTests` | Single class |
| `python manage.py makemigrations` | After model changes |
| `python manage.py migrate` | Apply migrations |
| `python manage.py createsuperuser` | Create admin |

## URLs

| URL | View | Namespace |
|---|---|---|
| `/` | Home | `pages` |
| `/accounts/login/` | Login | `accounts` |
| `/accounts/signup/` | SignUp | `accounts` |
| `/accounts/profile/update/` | Profile update | `accounts` |
| `/hotels/` | Hotel list | `hotels` |
| `/hotels/<id>/` | Hotel detail | `hotels` |
| `/hotels/create/` | Create hotel | `hotels` |
| `/hotels/<id>/edit/` | Update hotel | `hotels` |
| `/hotels/<id>/delete/` | Delete hotel | `hotels` |
| `/rooms/` | Room list | `rooms` |
| `/rooms/<id>/` | Room detail | `rooms` |
| `/rooms/create/` | Create room | `rooms` |
| `/rooms/<id>/edit/` | Update room | `rooms` |
| `/rooms/<id>/delete/` | Delete room | `rooms` |
| `/bookings/` | Booking list | `bookings` |
| `/bookings/create/` | Create booking | `bookings` |
| `/bookings/<id>/` | Booking detail | `bookings` |

## Models

**CustomUser** — email (unique, login field), username, phone_number, role (customer/owner).

**Profile** — OneToOne to user, address/city/country/postal_code/profile_picture.

**Hotel** — FK owner, name, description, address, city, country, phone_number (blank), email (blank), image (nullable), is_active, timestamps.

**Room** — FK hotel, room_number, room_type (choices), description (blank), price_per_night (Decimal), capacity, total/available_rooms, image (nullable), is_available, timestamps.

**Booking** — FK user + room, check_in/check_out, guests, total_price (auto-computed), status (pending/confirmed/cancelled/completed), timestamps.
