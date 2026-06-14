# Hotel Booking App

A Django-based hotel booking platform with user authentication, role-based access (customers and hotel owners), and profile management.

## Tech Stack

- **Python 3.13.5** / **Django 6.0.6**
- **SQLite** (development database)
- **Pillow** (profile picture uploads)
- Console email backend (password reset emails print to terminal)

## Features

### Authentication & User Management
- Custom user model (`CustomUser`) with email-based login
- Registration (signup) with username, email, phone number, and role selection
- Login / logout
- Password change and password reset (via console email)
- Role system: `customer` (default) or `owner` (hotel owner)

### Profile Management
- Each user gets an auto-created `Profile` via a signal
- Update profile: address, city, country, postal code, and profile picture
- Wired at `accounts/profile/update/`

### Pages
- Home page (`TemplateView` at `/`)

### Hotel Listings
- Browse hotels at `/hotels/` with search by name, filter by city, and sort by name or newest
- Full CRUD: create, detail, update, and delete — owner-only for create/edit/delete
- Paginated grid view (9 per page) with search/filter bar
- Role-gated: only `owner` users can manage hotels

### Room Listings
- Browse rooms at `/rooms/` with search by room number or hotel name, filter by room type
- Full CRUD: create, detail, update, and delete — owner-only for create/edit/delete
- Paginated grid view (12 per page) with search/filter bar
- Room model: hotel (FK), room number, type (single/double/deluxe/suite/family), description, price per night, capacity, total/available rooms, image
- Linked from hotel detail page (shows up to 3 rooms per hotel)

## Project Structure

```
hotel_booking/
├── accounts/              # Auth app (models, views, forms, urls, signals)
├── hotels/                # Hotels app (models, views, admin, urls)
│   └── templates/hotels/  # App-level templates (list, detail, form, confirm delete)
├── rooms/                 # Rooms app (models, views, admin, urls)
│   └── templates/rooms/   # App-level templates (list, detail, form, confirm delete)
├── pages/                 # Pages app (home page)
├── django_project/        # Project settings, root URL config
├── templates/             # Project-level templates
│   ├── base.html          # Base template with CSS variables
│   ├── home.html          # Home page
│   └── registration/      # Auth templates (login, signup, password reset, etc.)
├── media/                 # User-uploaded files (profile pictures, hotel images)
├── manage.py
└── requirements.txt
```

## Quick Start

```powershell
# Activate virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create a superuser (username + email + password required)
python manage.py createsuperuser

# Start dev server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser.

## Available Commands

```powershell
python manage.py runserver              # Dev server
python manage.py test                   # Run all tests (36 tests)
python manage.py test accounts          # Accounts app tests
python manage.py test pages             # Pages app tests
python manage.py test hotels            # Hotels app tests
python manage.py test rooms             # Rooms app tests
python manage.py makemigrations         # Create migrations after model changes
python manage.py migrate                # Apply migrations
python manage.py createsuperuser        # Create admin user
```

## URLs

### Auth

| URL | View | Template |
|-----|------|----------|
| `/accounts/login/` | LoginView | `registration/login.html` |
| `/accounts/logout/` | LogoutView | — |
| `/accounts/signup/` | SignUpView | `registration/signup.html` |
| `/accounts/profile/update/` | profile_update (custom) | `registration/profile_update.html` |
| `/accounts/password_change/` | PasswordChangeView | `registration/password_change_form.html` |
| `/accounts/password_change/done/` | PasswordChangeDoneView | `registration/password_change_done.html` |
| `/accounts/password_reset/` | PasswordResetView | `registration/password_reset_form.html` |
| `/accounts/password_reset/done/` | PasswordResetDoneView | `registration/password_reset_done.html` |
| `/accounts/reset/<uidb64>/<token>/` | PasswordResetConfirmView | `registration/password_reset_confirm.html` |
| `/accounts/reset/done/` | PasswordResetCompleteView | `registration/password_reset_complete.html` |

### Hotels

| URL | View | Template |
|-----|------|----------|
| `/hotels/` | HotelListView | `hotels/hotel_list.html` |
| `/hotels/<id>/` | HotelDetailView | `hotels/hotel_detail.html` |
| `/hotels/create/` | HotelCreateView | `hotels/hotel_form.html` |
| `/hotels/<id>/edit/` | HotelUpdateView | `hotels/hotel_form.html` |
| `/hotels/<id>/delete/` | HotelDeleteView | `hotels/hotel_confirm_delete.html` |

### Rooms

| URL | View | Template |
|-----|------|----------|
| `/rooms/` | RoomListView | `rooms/room_list.html` |
| `/rooms/<id>/` | RoomDetailView | `rooms/room_detail.html` |
| `/rooms/create/` | RoomCreateView | `rooms/room_form.html` |
| `/rooms/<id>/edit/` | RoomUpdateView | `rooms/room_form.html` |
| `/rooms/<id>/delete/` | RoomDeleteView | `rooms/room_confirm_delete.html` |

## Models

### CustomUser (extends AbstractUser)
- `email` — unique, used for login (`USERNAME_FIELD`)
- `phone_number` — optional
- `role` — `customer` or `owner` (default: `customer`)

### Profile (auto-created via signal)
- `user` — OneToOne to CustomUser
- `address`, `city`, `country`, `postal_code` — all optional
- `profile_picture` — ImageField (uploaded to `profiles/`)

### Hotel
- `owner` — FK to CustomUser (related_name `hotels`)
- `name`, `description`, `address`, `city`, `country`
- `phone_number`, `email` — both optional (blank)
- `image` — ImageField (uploaded to `hotels/`, nullable)
- `is_active`, `created_at`, `updated_at`

### Room
- `hotel` — FK to Hotel (related_name `rooms`)
- `room_number`, `room_type` (single/double/deluxe/suite/family)
- `description` — optional
- `price_per_night` — Decimal
- `capacity` — guests (default 1)
- `total_rooms`, `available_rooms` — counts (default 1)
- `image` — ImageField (uploaded to `rooms/`, nullable)
- `is_available`, `created_at`, `updated_at`
