from fpdf import FPDF
import os

class InterviewPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=25)
        self.add_font("Arial", "", r"C:\Windows\Fonts\arial.ttf", uni=True)
        self.add_font("Arial", "B", r"C:\Windows\Fonts\arialbd.ttf", uni=True)
        self.add_font("Arial", "I", r"C:\Windows\Fonts\ariali.ttf", uni=True)
        self.add_font("Arial", "BI", r"C:\Windows\Fonts\arialbi.ttf", uni=True)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Arial", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 8, "Hotel Booking Platform \u2014 Interview Preparation Guide", align="C")
            self.ln(4)
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)

    def footer(self):
        self.set_y(-20)
        self.set_font("Arial", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def chapter_title(self, title):
        self.set_font("Arial", "B", 18)
        self.set_text_color(30, 60, 114)
        self.cell(0, 12, title)
        self.ln(8)
        self.set_draw_color(30, 60, 114)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def section_title(self, title):
        self.set_x(self.l_margin)
        self.set_font("Arial", "B", 13)
        self.set_text_color(50, 50, 50)
        self.cell(0, 10, title)
        self.ln(7)

    def subsection_title(self, title):
        self.set_x(self.l_margin)
        self.set_font("Arial", "B", 11)
        self.set_text_color(70, 70, 70)
        self.cell(0, 9, title)
        self.ln(6)

    def body_text(self, text):
        self.set_x(self.l_margin)
        self.set_font("Arial", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet(self, text, indent=15):
        self.set_font("Arial", "", 10)
        self.set_text_color(40, 40, 40)
        self.set_x(self.l_margin + indent)
        self.cell(5, 5.5, "\u2022")
        self.cell(2, 5.5, "")
        w = self.w - self.r_margin - self.get_x()
        self.multi_cell(w, 5.5, text)

    def code_block(self, text):
        self.ln(2)
        self.set_fill_color(245, 245, 245)
        self.set_draw_color(200, 200, 200)
        self.set_font("Courier", "", 8.5)
        self.set_text_color(30, 30, 30)
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if i == 0:
                self.cell(2)
                self.cell(178, 5, line, border=1, fill=True)
            else:
                self.cell(2)
                self.cell(178, 5, line, border="LR", fill=True)
            self.ln()
        self.cell(2)
        self.cell(178, 5, "", border="B", fill=True)
        self.ln(4)

    def tip_box(self, text):
        self.ln(2)
        self.set_fill_color(230, 245, 230)
        self.set_draw_color(100, 180, 100)
        self.set_font("Arial", "B", 10)
        self.set_text_color(50, 130, 50)
        self.cell(3, 6, "", border=1, fill=True)
        self.set_fill_color(240, 250, 240)
        self.cell(177, 6, "  PRO TIP", border=1, fill=True)
        self.ln()
        self.set_font("Arial", "", 9.5)
        self.set_text_color(40, 40, 40)
        self.set_fill_color(245, 252, 245)
        self.multi_cell(180, 5.5, "  " + text, border=1, fill=True)
        self.ln(3)


def build_pdf():
    pdf = InterviewPDF()
    pdf.alias_nb_pages()

    # TITLE PAGE
    pdf.add_page()
    pdf.ln(50)
    pdf.set_font("Arial", "B", 30)
    pdf.set_text_color(30, 60, 114)
    pdf.cell(0, 14, "Hotel Booking Platform", align="C")
    pdf.ln(14)
    pdf.set_font("Arial", "", 16)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(0, 10, "Interview Preparation Guide", align="C")
    pdf.ln(20)
    pdf.set_draw_color(30, 60, 114)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(20)
    pdf.set_font("Arial", "", 11)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 7, "A full-stack Django 6.0 web application", align="C")
    pdf.ln(7)
    pdf.cell(0, 7, "Built with Python, Django ORM, SQLite/PostgreSQL, and Pillow", align="C")
    pdf.ln(30)
    pdf.set_font("Arial", "I", 10)
    pdf.cell(0, 7, "Use this guide to confidently present and discuss your project", align="C")

    # TABLE OF CONTENTS
    pdf.add_page()
    pdf.chapter_title("Table of Contents")
    toc = [
        ("1", "Project Overview & Elevator Pitch"),
        ("2", "Architecture & Design Decisions"),
        ("3", "Key Features & Walkthrough"),
        ("4", "Technical Highlights to Emphasize"),
        ("5", "Common Interview Questions & Answers"),
        ("6", "Code You Should Be Ready to Explain"),
        ("7", "Challenges & How You Solved Them"),
        ("8", "What You Learned & Future Improvements"),
        ("9", "Quick Reference Cheat Sheet"),
    ]
    for num, title in toc:
        pdf.set_font("Arial", "", 11)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(10, 8, num + ".")
        pdf.set_font("Arial", "", 11)
        pdf.cell(0, 8, title)
        pdf.ln(8)

    # SECTION 1
    pdf.add_page()
    pdf.chapter_title("1. Project Overview & Elevator Pitch")
    pdf.section_title("Elevator Pitch (30 seconds)")
    pdf.body_text(
        '"This is a Hotel Booking Platform built with Django 6.0. It is a full-stack web application '
        "that allows hotel owners to list and manage their properties, customers to browse hotels and rooms, "
        "make bookings, process payments, and leave reviews. It uses Django's ORM for all database operations, "
        "a custom user model with role-based authorization, and follows the MVT pattern with class-based views. "
        'The project has 7 Django apps, 179 automated tests, and is production-ready with deployment tooling for PythonAnywhere."'
    )
    pdf.ln(3)
    pdf.section_title("Project Overview (1 minute)")
    pdf.body_text(
        "The application serves two main user roles: hotel owners and customers. Owners can create and manage "
        "hotels and rooms. Customers can browse listings, filter by city/name/price, book rooms, make payments, "
        "and leave reviews. The project uses Django 6.0 with SQLite for development and PostgreSQL for production. "
        "Static files are served via WhiteNoise, and media files can use Cloudinary for production. The project "
        "includes a full test suite with 179 tests covering models, forms, views, and URL routing."
    )
    pdf.ln(3)
    pdf.section_title("Why This Project Matters")
    pdf.bullet("Demonstrates understanding of Django's full stack: models, views, templates, URLs, forms")
    pdf.bullet("Shows production awareness: deployment config, environment variables, separate dev/prod settings")
    pdf.bullet("Proves testing discipline: 179 tests across all 7 apps")
    pdf.bullet("Exhibits security awareness: role-based auth, user-scoped data access, CSRF protection")
    pdf.bullet("Covers real-world relational data: users, hotels, rooms, bookings, payments, reviews")

    # SECTION 2
    pdf.add_page()
    pdf.chapter_title("2. Architecture & Design Decisions")
    pdf.section_title("Seven Django Apps \u2014 Separation of Concerns")
    apps_info = [
        ("accounts", "Custom user auth, signup, profile, password management (email-based login)"),
        ("pages", "Home page with featured hotels and hero section"),
        ("hotels", "Hotel CRUD \u2014 owner-gated create/update/delete with public listing/detail"),
        ("rooms", "Room CRUD per hotel \u2014 owner-gated with public browse/filter"),
        ("bookings", "Booking CRUD per user \u2014 auto-computes total price"),
        ("payments", "Payment per booking (OneToOne) \u2014 auto-sets amount from booking"),
        ("reviews", "Reviews per hotel \u2014 one per user per hotel with UniqueConstraint"),
    ]
    for name, desc in apps_info:
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(30, 60, 114)
        pdf.cell(30, 6, name)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 6, desc)
        pdf.ln(1)

    pdf.ln(3)
    pdf.section_title("Data Model Relationships")
    pdf.body_text("CustomUser (1) <-> (1) Profile  |  User (1) -> (M) Booking  |  Hotel (1) -> (M) Room")
    pdf.body_text("Hotel (M) <- (1) Owner (User)  |  Booking (1) -> (1) Payment  |  Hotel (M) <- (1) User (Review)")
    pdf.body_text("Booking (M) <- (1) Room  |  Review (M) <- (1) User, Hotel")

    pdf.ln(3)
    pdf.section_title("Key Design Decisions")
    pdf.bullet("Custom User Model: Email-based login (USERNAME_FIELD = 'email'), keeps username in REQUIRED_FIELDS")
    pdf.bullet("Role-based authorization: 'customer' vs 'owner' role field; owner-gated via UserPassesTestMixin")
    pdf.bullet("Profile auto-creation: post_save signal on CustomUser creation")
    pdf.bullet("Class-based views throughout: DRY, consistent pattern, built-in pagination/form handling")
    pdf.bullet("Django 6.0 compatibility: uses updated django.conf.urls.static import, handles handle_no_permission changes")

    pdf.ln(3)
    pdf.section_title("Tech Stack")
    pdf.bullet("Backend: Python 3.13, Django 6.0, Django ORM, Whitenoise")
    pdf.bullet("Database: SQLite (dev) / PostgreSQL (prod) via dj-database-url")
    pdf.bullet("Image Processing: Pillow")
    pdf.bullet("Media Storage: FileSystemStorage (dev) / Cloudinary (prod)")
    pdf.bullet("Testing: Django TestCase (179 tests)")
    pdf.bullet("Deployment: PythonAnywhere WSGI with environment-based configuration")

    # SECTION 3
    pdf.add_page()
    pdf.chapter_title("3. Key Features & Walkthrough")
    pdf.section_title("How to Demo the Application")

    pdf.subsection_title("Feature 1 \u2014 Authentication & User Roles")
    pdf.body_text(
        "Users sign up with email, username, password, and select a role (customer or owner). "
        "Login is email-based. Owners can manage hotels/rooms. Customers browse, book, and review. "
        "Password reset uses console email backend for development."
    )
    pdf.code_block(
        "# CustomUser model\n"
        "class CustomUser(AbstractUser):\n"
        "    email = models.EmailField(unique=True)\n"
        "    role = models.CharField(max_length=10,\n"
        "        choices=[('customer', 'Customer'), ('owner', 'Owner')],\n"
        '        default="customer")\n'
        "    USERNAME_FIELD = 'email'\n"
        "    REQUIRED_FIELDS = ['username']"
    )

    pdf.subsection_title("Feature 2 \u2014 Hotel & Room Management (Owner)")
    pdf.body_text(
        "Owners create hotels with name, description, address, city, country, and image. "
        "Each hotel can have multiple rooms with types (single/double/deluxe/suite/family), "
        "pricing, and availability tracking. Owner-only views use UserPassesTestMixin."
    )

    pdf.subsection_title("Feature 3 \u2014 Search, Filter & Sort (Public)")
    pdf.body_text(
        "HotelListView supports search by name, filter by city, and sort by name or newest. "
        "RoomListView supports search by room number or hotel name, filter by room type and hotel. "
        "Both use Django ORM querysets with pagination (9 per page for hotels, 12 for rooms)."
    )

    pdf.subsection_title("Feature 4 \u2014 Booking with Price Computation")
    pdf.body_text(
        "Customers select a room, choose dates and guest count. The system computes "
        "total_price = room.price_per_night * (check_out - check_in). Bookings have status "
        "tracking (pending/confirmed/cancelled/completed). Users see only their own bookings."
    )
    pdf.code_block(
        "# Auto-compute total price on booking\n"
        "def form_valid(self, form):\n"
        "    days = (form.instance.check_out - form.instance.check_in).days\n"
        "    form.instance.total_price = form.instance.room.price_per_night * days\n"
        "    return super().form_valid(form)"
    )

    pdf.subsection_title("Feature 5 \u2014 Payments (One-to-One)")
    pdf.body_text(
        "Each booking can have exactly one payment. Payment view auto-sets amount from "
        "the booking's total_price, validates booking ownership, and prevents duplicate payments. "
        "Supports multiple methods: card, PayPal, bank transfer, cash."
    )

    pdf.subsection_title("Feature 6 \u2014 Reviews with Uniqueness Constraint")
    pdf.body_text(
        "Authenticated users can leave one review per hotel (enforced by database-level "
        "UniqueConstraint). Ratings are 1-5. Reviews display inline on the hotel detail page. "
        "Duplicate review attempts redirect to the edit view."
    )
    pdf.code_block(
        "# UniqueConstraint for one review per user per hotel\n"
        "class Meta:\n"
        "    ordering = ['-created_at']\n"
        "    constraints = [\n"
        "        models.UniqueConstraint(\n"
        "            fields=['user', 'hotel'],\n"
        "            name='unique_user_hotel_review'\n"
        "        )\n"
        "    ]"
    )

    # SECTION 4
    pdf.add_page()
    pdf.chapter_title("4. Technical Highlights to Emphasize")
    pdf.tip_box(
        "Mention these points naturally during your walkthrough. They show depth beyond basic CRUD."
    )
    pdf.ln(2)

    highlights = [
        ("Django 6.0 Awareness",
         "You're using the latest Django. You know about the updated django.conf.urls.static import, "
         "the handle_no_permission change in AccessMixin, and ImageField behavior returning ImageFieldFile when empty."),
        ("Production-Ready Configuration",
         "Environment variables for SECRET_KEY, DEBUG, ALLOWED_HOSTS, DATABASE_URL, and Cloudinary. "
         "WhiteNoise for static files. Separate dev/prod media storage. PythonAnywhere WSGI script."),
        ("Role-Based Authorization",
         "Two-tier access: customer vs owner. Owner-gated CRUD via UserPassesTestMixin + LoginRequiredMixin. "
         "User-scoped data access (users see only their bookings/payments). Django 6.0 handle_no_permission override."),
        ("Comprehensive Test Suite",
         "179 tests across 7 apps. Tests cover models, forms, views, URLs, permissions, edge cases. "
         "Run with: python manage.py test (parallel mode available)."),
        ("Database Constraints",
         "PostgreSQL-ready via dj-database-url. UniqueConstraint for one-review-per-user-per-hotel. "
         "ForeignKey relationships with proper related_name. Null-safe image handling."),
        ("Clean Template Architecture",
         "Project-level base.html with inlined CSS and CSS variables. App-level templates per concerns. "
         "Forms use consistent form-control widget class. Mobile-responsive nav with hamburger menu."),
        ("Class-Based Views Throughout",
         "Consistent use of generic views (ListView, DetailView, CreateView, UpdateView, DeleteView). "
         "Built-in pagination, form validation, permission checks. DRY pattern across all apps."),
    ]
    for title, desc in highlights:
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(30, 60, 114)
        pdf.cell(0, 6, title)
        pdf.ln(6)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 5.5, desc)
        pdf.ln(3)

    # SECTION 5
    pdf.add_page()
    pdf.chapter_title("5. Common Interview Questions & Answers")

    qas = [
        ("Q: Why Django for this project?",
         "Django's ORM, built-in admin, authentication system, and class-based views made it ideal. "
         "It provides batteries-included security (CSRF, XSS protection) and scales well. "
         "The MVT pattern maps naturally to web applications with database relationships."),
        ("Q: How did you handle user authentication?",
         "I used a custom user model extending AbstractUser with email as the login field. "
         "Users have roles (customer/owner). Profiles are auto-created via a post_save signal. "
         "Password management uses Django's built-in views for reset and change."),
        ("Q: How does authorization work?",
         "Two levels: role-based (owner vs customer) using UserPassesTestMixin, and "
         "user-scoped (users only see their own bookings/payments) using manual checks. "
         "For owner-gated views, I combine LoginRequiredMixin with UserPassesTestMixin "
         "and override handle_no_permission to redirect with a message instead of raising PermissionDenied."),
        ("Q: How did you structure the database?",
         "Six models across seven apps. CustomUser -> Profile (one-to-one), Hotel -> Room (one-to-many), "
         "User -> Booking (one-to-many), Room -> Booking (one-to-many), Booking -> Payment (one-to-one), "
         "and User+Hotel -> Review (unique constraint). Using Django ORM with proper foreign keys "
         "and related_names for efficient querying."),
        ("Q: How did you test the application?",
         "I wrote 179 tests using Django's TestCase. Each app has dedicated test files covering "
         "models (creation, string representation, defaults, constraints), forms (validation, widgets), "
         "views (URL resolution, templates, permissions, context data), and edge cases (404s, "
         "duplicate entries, unauthenticated access). I can run them with python manage.py test."),
        ("Q: What challenges did you face?",
         "One challenge was Django 6.0's change to handle_no_permission in AccessMixin which now raises "
         "PermissionDenied for authenticated users who fail test_func(). I had to override it with "
         "proper is_authenticated checking. Another was ImageField returning ImageFieldFile wrapper "
         "instead of None when empty, which required adjusting test assertions."),
        ("Q: How would you extend this project?",
         "I would add real payment gateway integration (Stripe), email notifications via SendGrid, "
         "availability validation during booking (checking overlapping dates), an API layer with DRF, "
         "and a real-time notification system using Django Channels or WebSockets."),
        ("Q: How is this production-ready?",
         "The settings use environment variables for all sensitive config. WhiteNoise serves static files. "
         "PostgreSQL can replace SQLite via DATABASE_URL. Media can use Cloudinary. The project has "
         "a PythonAnywhere WSGI entry point. Security settings like SECURE_HSTS and CSRF_COOKIE_SECURE "
         "are toggled based on DEBUG mode."),
        ("Q: Walk me through a booking request lifecycle.",
         "A user selects a room and submits the booking form. BookingCreateView validates the form, "
         "computes total_price = price_per_night * days in form_valid(), and saves the booking. "
         "The user then creates a payment via PaymentCreateView, which auto-sets amount from "
         "booking.total_price and validates ownership. Both views use LoginRequiredMixin. "
         "The booking shows up in their booking list, ordered by most recent."),
        ("Q: How did you manage the git workflow?",
         "I used a standard git workflow with meaningful commits. The project is version-controlled "
         "locally. I made atomic commits for features like 'Add hotel model and CRUD views' or "
         "'Add booking with price computation'. The .gitignore excludes pyc files, media uploads, "
         "virtual environment, and the SQLite database."),
        ("Q: What would you improve with more time?",
         "I'd add availability validation to prevent double-booking, integrate a real payment "
         "gateway, add email notifications for booking confirmations, implement an admin dashboard "
         "with analytics, write more comprehensive tests for edge cases, add Django REST Framework "
         "for mobile app support, and improve the UI with a frontend framework like HTMX."),
    ]

    for q, a in qas:
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(30, 60, 114)
        pdf.multi_cell(0, 6, q)
        pdf.ln(1)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 5.5, a)
        pdf.ln(4)

    # SECTION 6
    pdf.add_page()
    pdf.chapter_title("6. Code You Should Be Ready to Explain")
    pdf.body_text(
        "Be prepared to walk through these code snippets. Read them aloud and explain each line."
    )

    pdf.section_title("1. Custom User Model (accounts/models.py)")
    pdf.code_block(
        "class CustomUser(AbstractUser):\n"
        "    email = models.EmailField(unique=True)\n"
        "    phone_number = models.CharField(max_length=15, blank=True)\n"
        "    role = models.CharField(\n"
        "        max_length=10,\n"
        "        choices=[('customer', 'Customer'), ('owner', 'Owner')],\n"
        "        default='customer'\n"
        "    )\n"
        "    USERNAME_FIELD = 'email'\n"
        "    REQUIRED_FIELDS = ['username']\n"
        "\n"
        "    def __str__(self):\n"
        "        return self.email"
    )
    pdf.body_text("Why: Email-based login is more practical. Role field enables authorization. Username kept for Django compatibility.")

    pdf.section_title("2. Owner-Gated View (hotels/views.py)")
    pdf.code_block(
        "class HotelCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):\n"
        "    model = Hotel\n"
        "    form_class = HotelForm\n"
        "    template_name = 'hotels/hotel_form.html'\n"
        "    success_url = reverse_lazy('hotels:hotel_list')\n"
        "\n"
        "    def test_func(self):\n"
        "        return self.request.user.role == 'owner'\n"
        "\n"
        "    def handle_no_permission(self):\n"
        "        if not self.request.user.is_authenticated:\n"
        "            return redirect('login')\n"
        "        messages.error(self.request, 'Only owners can create hotels.')\n"
        "        return redirect('home')\n"
        "\n"
        "    def form_valid(self, form):\n"
        "        form.instance.owner = self.request.user\n"
        "        return super().form_valid(form)"
    )
    pdf.body_text("Why: Shows understanding of Django's mixin-based permission system. handle_no_permission is a Django 6.0 nuance.")

    pdf.section_title("3. Booking with Price Auto-Compute (bookings/views.py)")
    pdf.code_block(
        "class BookingCreateView(LoginRequiredMixin, CreateView):\n"
        "    model = Booking\n"
        "    form_class = BookingForm\n"
        "    template_name = 'bookings/booking_form.html'\n"
        "    success_url = reverse_lazy('bookings:booking_list')\n"
        "\n"
        "    def get_initial(self):\n"
        "        initial = super().get_initial()\n"
        "        room_id = self.request.GET.get('room')\n"
        "        if room_id:\n"
        "            initial['room'] = room_id\n"
        "        return initial\n"
        "\n"
        "    def form_valid(self, form):\n"
        "        form.instance.user = self.request.user\n"
        "        days = (form.instance.check_out - form.instance.check_in).days\n"
        "        form.instance.total_price = form.instance.room.price_per_night * days\n"
        "        return super().form_valid(form)"
    )
    pdf.body_text("Why: Shows business logic integration (price computation), pre-selection from URL params, and user assignment.")

    pdf.section_title("4. UniqueConstraint for Reviews (reviews/models.py)")
    pdf.code_block(
        "class Review(models.Model):\n"
        "    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='reviews')\n"
        "    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='reviews')\n"
        "    rating = models.PositiveSmallIntegerField(choices=[(i, i) for i in range(1, 6)])\n"
        "    comment = models.TextField()\n"
        "    created_at = models.DateTimeField(auto_now_add=True)\n"
        "    updated_at = models.DateTimeField(auto_now=True)\n"
        "\n"
        "    class Meta:\n"
        "        ordering = ['-created_at']\n"
        "        constraints = [\n"
        "            models.UniqueConstraint(\n"
        "                fields=['user', 'hotel'],\n"
        "                name='unique_user_hotel_review'\n"
        "            )\n"
        "        ]"
    )
    pdf.body_text("Why: Database-level constraint ensures data integrity. Shows understanding of Meta options and constraints.")

    # SECTION 7
    pdf.add_page()
    pdf.chapter_title("7. Challenges & How You Solved Them")
    pdf.body_text("Interviewers love hearing about real problems you solved. Be ready with these:")

    challenges = [
        ("Django 6.0 handle_no_permission Change",
         "In Django 6.0, AccessMixin raises PermissionDenied for authenticated users who fail test_func(), even without "
         "raise_exception=True. This caused owners-only views to crash instead of redirect. I overrode handle_no_permission "
         "to check is_authenticated first, sending customers to login if unauthenticated or showing a message if authenticated."),
        ("ImageField Returning Wrapper Instead of None",
         "When testing, I discovered that an empty ImageField returns an ImageFieldFile wrapper, not None. "
         "This broke assertions. I changed tests from assertIsNone to assertFalse to handle this Django 6.0 behavior."),
        ("One Review Per User Per Hotel",
         "I needed to ensure users can only leave one review per hotel. I implemented this with a database-level "
         "UniqueConstraint and also handled it at the view level by checking for existing reviews and redirecting to edit."),
        ("Preventing Duplicate Payments",
         "Each booking should have only one payment. I added a check in PaymentCreateView that redirects "
         "if a payment already exists for the booking, preventing duplicate payment entries."),
        ("Profile Null Safety",
         "The profile_update view needed to handle cases where a profile might not exist (edge case from database manipulation). "
         "I added a try-except for Profile.DoesNotExist that creates the profile on the fly if missing."),
    ]

    for title, desc in challenges:
        pdf.set_font("Arial", "B", 10)
        pdf.set_text_color(180, 60, 30)
        pdf.cell(0, 6, title)
        pdf.ln(6)
        pdf.set_font("Arial", "", 10)
        pdf.set_text_color(40, 40, 40)
        pdf.multi_cell(0, 5.5, desc)
        pdf.ln(3)

    # SECTION 8
    pdf.add_page()
    pdf.chapter_title("8. What You Learned & Future Improvements")

    pdf.section_title("Skills Demonstrated")
    skills = [
        "Full-stack Django development with MVT architecture",
        "Database modeling with relational constraints and custom user models",
        "Role-based authorization and user-scoped data access",
        "Class-based views with mixins for DRY permission handling",
        "Django form handling, validation, and widget customization",
        "Writing comprehensive tests (179 tests across 7 apps)",
        "Production deployment considerations (environment variables, static files, WSGI)",
        "Git version control with atomic commits",
    ]
    for s in skills:
        pdf.bullet(s)

    pdf.ln(4)
    pdf.section_title("Future Improvements (Talk About These Ambitions)")
    futures = [
        "Real payment gateway integration (Stripe/PayPal)",
        "Availability validation \u2014 check overlapping booking dates",
        "Email notifications via SendGrid or Amazon SES",
        "REST API with Django REST Framework for mobile/web clients",
        "Docker containerization for consistent environments",
        "CI/CD pipeline with GitHub Actions (run tests, lint, deploy)",
        "Admin dashboard with booking analytics and charts",
        "Wishlist/favorites feature for users to save hotels",
        "HTMX integration for dynamic updates without full page reloads",
        "Internationalization (i18n) for multi-language support",
    ]
    for f in futures:
        pdf.bullet(f)

    # SECTION 9
    pdf.add_page()
    pdf.chapter_title("9. Quick Reference Cheat Sheet")
    pdf.body_text("Memorize these numbers and commands for quick recall during the interview.")

    pdf.section_title("Key Numbers")
    metrics = [
        ("Languages/Frameworks", "Python 3.13, Django 6.0, JavaScript (vanilla)"),
        ("Django Apps", "7 (accounts, pages, hotels, rooms, bookings, payments, reviews)"),
        ("Database Models", "6 (CustomUser, Profile, Hotel, Room, Booking, Payment, Review)"),
        ("Tests", "179 across 7 test files"),
        ("Dependencies", "11 (Django, Pillow, Whitenoise, dj-database-url, psycopg2, Cloudinary, etc.)"),
        ("Templates", "19 (1 base + 18 app/project templates)"),
        ("User Roles", "2 (customer, owner)"),
    ]
    for label, val in metrics:
        pdf.set_font("Arial", "B", 9)
        pdf.set_text_color(60, 60, 60)
        pdf.cell(55, 5.5, label + ":")
        pdf.set_font("Arial", "", 9)
        pdf.cell(0, 5.5, val)
        pdf.ln(5.5)

    pdf.ln(4)
    pdf.section_title("Key Commands")
    cmds = [
        ("Run server", "python manage.py runserver"),
        ("All tests", "python manage.py test"),
        ("Parallel tests", "python manage.py test --parallel"),
        ("Single app test", "python manage.py test hotels"),
        ("Single test class", "python manage.py test bookings.tests.BookingCreateViewTests"),
        ("Migrations", "python manage.py makemigrations  /  migrate"),
        ("Superuser", "python manage.py createsuperuser"),
        ("Activate venv", ".venv\\Scripts\\Activate.ps1"),
    ]
    for label, cmd in cmds:
        pdf.set_font("Courier", "", 9)
        pdf.set_text_color(40, 40, 40)
        pdf.cell(40, 5.5, label + ":")
        pdf.cell(0, 5.5, cmd)
        pdf.ln(5.5)

    pdf.ln(4)
    pdf.section_title("Framing Your Answers \u2014 STAR Method")
    pdf.body_text(
        "When answering behavioral questions, use the STAR method:"
    )
    pdf.bullet("Situation: 'We needed a hotel booking platform with role-based access...'")
    pdf.bullet("Task: 'I was responsible for designing the database and implementing the booking flow...'")
    pdf.bullet("Action: 'I created 7 Django apps, each with specific responsibilities, and wrote 179 tests...'")
    pdf.bullet("Result: 'The project is fully functional with role-based access, search/filter, automated pricing, and a production-ready deployment setup.'")

    pdf.ln(6)
    pdf.tip_box(
        'Confidence matters more than perfection. If you don\'t know something, say '
        '"I haven\'t encountered that yet, but here\'s how I would approach it..."'
    )

    output_path = os.path.join(os.path.dirname(__file__), "Hotel_Booking_Interview_Guide.pdf")
    pdf.output(output_path)
    return output_path

if __name__ == "__main__":
    path = build_pdf()
    print(f"PDF created: {path}")
