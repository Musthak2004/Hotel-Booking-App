<div align="center">
  <h1>🏨 Hotel Booking Platform</h1>
  <p><strong>A full-featured Django 6.0 hotel booking system with Stripe payments, owner dashboard, seasonal pricing, promo codes, REST API, and CI/CD.</strong></p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.12-blue" alt="Python 3.12">
    <img src="https://img.shields.io/badge/Django-6.0-green" alt="Django 6.0">
    <img src="https://img.shields.io/badge/tests-233_✓-brightgreen" alt="233 tests passing">
  </p>
</div>

---

## ✨ Features

### 👤 Authentication & Roles
- **Email-based login** via `CustomUser` model (`USERNAME_FIELD = "email"`)
- Two user roles: **Customer** and **Hotel Owner**
- Full password reset flow (emails to console in development)
- User profile with picture upload, address, and contact details

### 🏨 Hotel Management
- CRUD operations for hotels — only hotel owners can create/edit/delete their listings
- Rich filtering: text search, city, country, amenities, price range, guest capacity, date availability
- Sorting by name or newest, paginated grid (9 per page)
- Hotel detail page with inline rooms, reviews, gallery, and amenity badges
- Amenities system with M2M relationship and amenity-based filtering

### 🛏️ Room Management
- CRUD per hotel with owner-gated permissions
- Room types: Single, Double, Deluxe, Suite, Family
- Availability tracking computed dynamically from active bookings
- **Seasonal pricing rules** via `PriceRule` model
- Date-range availability search
- Row-level lock (`select_for_update()`) to prevent booking race conditions

### 📅 Bookings
- Automatic `total_price` calculation (`price_per_night × nights`)
- **Promo codes** — percentage-based discounts with usage limits and validity windows
- **Seasonal pricing** — price rules auto-applied when dates overlap
- **Race condition safe** — wrapped in `transaction.atomic` + row-level lock
- User-scoped booking list and detail views
- **Cancellation flow** with optional Stripe refund integration
- Status tracking: Pending → Confirmed → Completed / Cancelled

### 💳 Payments (Stripe Integration)
- Stripe Checkout Session creation with line-item details
- Webhook handler for `checkout.session.completed` — confirms booking, sends receipts
- Automatic refund on cancellation for paid bookings
- Success and cancelled landing pages
- **7 webhook test scenarios**: valid payload, duplicate idempotency, invalid signature, bad payload, missing secret, unknown booking, unhandled event type

### ⭐ Reviews
- One review per user per hotel (enforced via `UniqueConstraint`)
- 1–5 star rating system
- Create, edit, and delete your own reviews
- Reviews displayed inline on hotel detail pages with edit timestamps

### 📊 Owner Dashboard
- Stats cards: total hotels, rooms, bookings, active bookings, revenue
- Recent bookings table (last 10 across all hotels with user + room details)
- Per-hotel summary: room count, booking count, active bookings, revenue

### ❤️ Wishlist / Saved Hotels
- Toggle hotels in/out of saved list via AJAX-friendly POST endpoint
- Dedicated wishlist page (`/accounts/wishlist/`) with grid layout
- Visual heart indicator on hotel detail page

### 🖼️ Multi-Image Gallery
- Gallery models for both hotels (`HotelImage`) and rooms (`RoomImage`)
- Each image has ordering, primary flag, and separate upload directory
- Horizontal scrollable strip on detail pages

### 📧 Email Notifications
| Event | Recipients | Templates |
|---|---|---|
| Booking confirmed | Customer + Hotel Owner | HTML + plain text |
| Booking cancelled | Customer | HTML + plain text |
| Payment receipt | Customer | HTML + plain text |
- Console backend in development; SMTP-configurable for production via `SITE_URL`

### 🔌 REST API (DRF)
- Read-only endpoints: `/api/hotels/` (list/detail), `/api/rooms/` (list/detail)
- Hotel detail includes nested rooms
- Room filtering by type, hotel ID, price range
- Search filtering by name, city, country, description
- Browsable API enabled for convenient debugging

### 🛡️ CI/CD
- GitHub Actions workflow on push/PR to `main`
- Python 3.12 + PostgreSQL 16 test runner
- Automatic migration consistency check (`makemigrations --check`)
- 233 automated tests spanning all seven apps

---

## 🧱 Architecture

### Project Structure

```
hotel_booking/
├── accounts/              # CustomUser, Profile, auth views, wishlist
│   ├── templates/
│   │   └── accounts/      # wishlist.html
│   └── migrations/
├── api/                   # DRF read-only API (HotelViewSet, RoomViewSet)
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── bookings/              # Booking CRUD, cancellation, promo codes
│   ├── emails.py          # send_booking_confirmation / cancellation
│   ├── templates/bookings/
│   └── migrations/
├── django_project/        # Settings, root URL conf, WSGI
├── hotels/                # Hotel CRUD, amenities, gallery, dashboard
│   ├── management/
│   │   └── commands/       # seed_data.py
│   ├── templates/hotels/
│   └── migrations/
├── pages/                 # Home page with featured hotels
│   └── templates/
├── payments/              # Stripe checkout, webhooks, emails
│   ├── services.py        # create_checkout_session()
│   ├── webhooks.py        # stripe_webhook handler
│   ├── emails.py          # send_payment_receipt()
│   ├── templates/payments/
│   └── migrations/
├── reviews/               # Review CRUD (1 per user per hotel)
│   └── templates/reviews/
├── rooms/                 # Room CRUD, PriceRule, gallery
│   ├── templates/rooms/
│   └── migrations/
├── templates/             # Base template, home, shared templates
│   ├── emails/            # HTML + TXT email templates
│   └── registration/      # Login, signup, password reset templates
├── media/                 # User uploads (gitignored)
├── staticfiles/           # collectstatic output (gitignored)
├── .github/
│   └── workflows/         # CI pipeline
├── manage.py
└── requirements.txt
```

### Data Model

| Model | Key Fields | Relationships |
|---|---|---|
| `CustomUser` | email (`USERNAME_FIELD`), role, phone_number, saved_hotels | Extends `AbstractUser`, M2M → `Hotel` |
| `Profile` | user, address, city, country, postal_code, profile_picture | OneToOne → `CustomUser` |
| `Hotel` | owner, name, description, address, city, country, phone, email, image, is_active | FK → `CustomUser`, M2M → `Amenity` |
| `HotelImage` | hotel, image, is_primary, order | FK → `Hotel` |
| `Amenity` | name, icon | M2M → `Hotel` |
| `Room` | hotel, room_number, room_type, price_per_night, capacity, total_rooms, image, is_available | FK → `Hotel` |
| `RoomImage` | room, image, is_primary, order | FK → `Room` |
| `PriceRule` | room, name, start_date, end_date, price_per_night | FK → `Room` |
| `Booking` | user, room, check_in, check_out, guests, total_price, status | FK → `User`, FK → `Room` |
| `PromoCode` | code, discount_percent, max_uses, used_count, valid_from, valid_until, is_active | Standalone |
| `Payment` | booking, amount, payment_method, transaction_id, stripe_session_id, status, paid_at | OneToOne → `Booking` |
| `Review` | user, hotel, rating, comment | FK → `User`, FK → `Hotel` (UniqueConstraint) |

### URL Map

| Namespace | URL | View | Description |
|---|---|---|---|
| **pages** | `/` | Home page | Featured hotels grid + search |
| **accounts** | `/accounts/login/` | LoginView | Email-based login |
| | `/accounts/signup/` | SignUpView | User registration |
| | `/accounts/profile/update/` | profile_update | Edit profile + picture |
| | `/accounts/wishlist/` | SavedHotelsListView | Saved hotels grid |
| | `/accounts/password_change/` | PasswordChangeView | Change password |
| | `/accounts/password_reset/` | PasswordResetView | Reset password by email |
| **hotels** | `/hotels/` | HotelListView | Paginated, filtered list |
| | `/hotels/<id>/` | HotelDetailView | Rooms + reviews + gallery |
| | `/hotels/create/` | HotelCreateView | Owner only |
| | `/hotels/<id>/edit/` | HotelUpdateView | Own hotel only |
| | `/hotels/<id>/delete/` | HotelDeleteView | Own hotel only |
| | `/hotels/owner/dashboard/` | OwnerDashboardView | Stats + recent bookings |
| | `/hotels/<id>/wishlist/toggle/` | ToggleWishlistView | POST toggle |
| **rooms** | `/rooms/` | RoomListView | Available, filtered, paginated |
| | `/rooms/<id>/` | RoomDetailView | Room details + gallery |
| | `/rooms/create/` | RoomCreateView | Owner only |
| | `/rooms/<id>/edit/` | RoomUpdateView | Own hotel only |
| | `/rooms/<id>/delete/` | RoomDeleteView | Own hotel only |
| **bookings** | `/bookings/` | BookingListView | User's bookings |
| | `/bookings/create/` | BookingCreateView | Auto-calculates price |
| | `/bookings/<id>/` | BookingDetailView | Booking details + payment |
| | `/bookings/<id>/cancel/` | BookingCancelView | Confirmation + refund |
| **payments** | `/payments/checkout/<booking_id>/` | PaymentCheckoutView | Stripe redirect |
| | `/payments/success/<booking_id>/` | PaymentSuccessView | Success page |
| | `/payments/cancelled/<booking_id>/` | PaymentCancelledView | Cancelled page |
| | `/payments/<id>/` | PaymentDetailView | Receipt details |
| | `/payments/webhook/` | stripe_webhook | Stripe event handler |
| **reviews** | `/reviews/create/<hotel_id>/` | ReviewCreateView | One per user per hotel |
| | `/reviews/<id>/edit/` | ReviewUpdateView | Own review only |
| | `/reviews/<id>/delete/` | ReviewDeleteView | Own review only |
| **api** | `/api/hotels/` | HotelViewSet | Read-only, browsable |
| | `/api/rooms/` | RoomViewSet | Filterable, browsable |
| | `/health/` | healthcheck | Health check endpoint |
| | `/debug-db/` | debug_db | Database connectivity check |

### Permissions Model

| Role | Capabilities |
|---|---|
| **Unauthenticated** | Browse hotels and rooms |
| **Customer** | All browse + create bookings, write/edit/delete own reviews, save wishlist, make payments, cancel own bookings |
| **Hotel Owner** | All customer actions + create/edit/delete hotels and rooms, view owner dashboard |

> **Django 6.0 note:** `AccessMixin` raises `PermissionDenied` for authenticated users who fail `test_func()` even without `raise_exception=True`. All handler views override `handle_no_permission` with `messages.error()` + `redirect()`.

### Frontend
- **Server-rendered Django templates** (no JS framework)
- Pure CSS design with CSS custom properties (Inter font via Google Fonts)
- Consistent design system: `.btn`, `.btn-primary`, `.form-card`, `.detail-grid`, `.card` patterns
- Responsive layouts with mobile breakpoints
- Toast-style `messages` framework for user notifications

---

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/hotel-booking.git
cd hotel_booking

# 2. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment variables and edit as needed
cp .env.example .env

# 5. Run migrations
python manage.py migrate

# 6. Create a superuser
python manage.py createsuperuser

# 7. (Optional) Seed sample data
python manage.py seed_data

# 8. Start the development server
python manage.py runserver
```

Visit **http://127.0.0.1:8000** in your browser.

---

## 🧪 Testing

```bash
# Run all 233 tests
python manage.py test

# Test a single app
python manage.py test hotels
python manage.py test rooms
python manage.py test bookings
python manage.py test payments
python manage.py test reviews
python manage.py test accounts
python manage.py test api

# Test a single class
python manage.py test bookings.tests.BookingCreateViewTests

# Test a single method
python manage.py test rooms.tests.RoomModelTests.test_create_room

# Check for missing migrations
python manage.py makemigrations --check --dry-run
```

### Test Coverage by App

| App | Focus |
|---|---|
| `accounts` | Auth, signup, profile update, wishlist |
| `hotels` | Model, form, list/detail/create/update/delete views, ratings, messages, empty states |
| `rooms` | Model, form, list/detail/create/update/delete views, availability logic, messages |
| `bookings` | Model, form, create/list/detail/cancel views, messages, cancellation with refund |
| `payments` | Model, form, checkout/success/cancelled/detail views, **Stripe webhooks (7 scenarios)** |
| `reviews` | Model, form, create/update/delete views, messages, duplicate prevention |
| `api` | DRF endpoint availability and response structure |

---

## ⚙️ Configuration

### Environment Variables (`.env`)

| Variable | Required | Default | Description |
|---|---|---|---|
| `DJANGO_SECRET_KEY` | Yes | — | Django secret key |
| `DJANGO_DEBUG` | No | `False` | Debug mode (`True`/`False`) |
| `DJANGO_ALLOWED_HOSTS` | No | `localhost,127.0.0.1` | Comma-separated hosts |
| `DATABASE_URL` | No | SQLite | PostgreSQL connection string |
| `CLOUDINARY_URL` | No | Local files | Cloudinary media storage URL |
| `STRIPE_PUBLISHABLE_KEY` | For payments | — | Stripe publishable key |
| `STRIPE_SECRET_KEY` | For payments | — | Stripe secret key |
| `STRIPE_WEBHOOK_SECRET` | For webhooks | — | Stripe webhook signing secret |
| `SITE_URL` | For emails | — | Production URL for email links |

### Production Checklist

- [ ] Set `DJANGO_SECRET_KEY` to a strong, unique value
- [ ] Set `DJANGO_DEBUG=False`
- [ ] Set `DJANGO_ALLOWED_HOSTS` to your domain(s)
- [ ] Configure a production database via `DATABASE_URL`
- [ ] Set Stripe keys for payment processing
- [ ] Configure `SITE_URL` for email links
- [ ] Switch `EMAIL_BACKEND` to SMTP with proper credentials
- [ ] Enable Cloudinary or set up persistent media storage
- [ ] Run `python manage.py collectstatic --noinput`

---

## 🚢 Deployment

### PythonAnywhere

```bash
# On PythonAnywhere Bash console:
cd ~/your-project
git pull
workon your-venv         # Activate your virtualenv
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Reload the web app (or click "Reload" on the Web tab):
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

### Docker (manual)

```bash
# Build and run with PostgreSQL
docker compose up --build
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | Django 6.0.6 |
| **Language** | Python 3.12 |
| **Database** | SQLite (dev) / PostgreSQL (prod) via `dj-database-url` |
| **Frontend** | Server-rendered Django templates, inline CSS, Inter font |
| **Payments** | Stripe Checkout Sessions + Webhooks |
| **Media Storage** | Local filesystem or Cloudinary |
| **Static Files** | Whitenoise 6.9 (`CompressedManifestStaticFilesStorage` in production) |
| **API** | Django REST Framework 3.17+ (read-only viewsets) |
| **CI/CD** | GitHub Actions (push/PR → test on PostgreSQL 16) |

### Dependencies

```
Django==6.0.6           # Web framework
Pillow                  # Image processing
whitenoise==6.9         # Static file serving
dj-database-url         # Database URL parsing
psycopg2-binary         # PostgreSQL adapter
stripe>=18.0.0          # Payment processing
djangorestframework>=3.17.1  # REST API
django-cloudinary-storage  # Cloudinary media (optional)
cloudinary              # Cloudinary SDK (optional)
```

---

## 📋 License

This project is licensed under the MIT License.
