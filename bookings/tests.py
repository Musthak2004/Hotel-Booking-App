from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from hotels.models import Hotel
from rooms.models import Room
from .models import Booking
from .forms import BookingForm
from .views import BookingCreateView, BookingListView, BookingDetailView

User = get_user_model()


class BookingModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="double",
            price_per_night=150, capacity=2
        )

    def test_create_booking(self):
        booking = Booking.objects.create(
            user=self.user,
            room=self.room,
            check_in=date(2026, 7, 1),
            check_out=date(2026, 7, 5),
            guests=2,
            total_price=600,
        )
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.room, self.room)
        self.assertEqual(booking.guests, 2)
        self.assertEqual(booking.total_price, 600)
        self.assertEqual(booking.status, "pending")

    def test_string_representation(self):
        booking = Booking.objects.create(
            user=self.user, room=self.room,
            check_in=date(2026, 7, 1), check_out=date(2026, 7, 5),
            guests=1, total_price=600,
        )
        self.assertIn(self.user.email, str(booking))
        self.assertIn(str(self.room), str(booking))

    def test_default_status_pending(self):
        booking = Booking.objects.create(
            user=self.user, room=self.room,
            check_in=date(2026, 7, 1), check_out=date(2026, 7, 5),
            guests=1, total_price=600,
        )
        self.assertEqual(booking.status, "pending")


class BookingFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="double",
            price_per_night=150, capacity=2
        )

    def test_form_valid_data(self):
        form = BookingForm(data={
            "room": self.room.id,
            "check_in": "2026-07-01",
            "check_out": "2026-07-05",
            "guests": 2,
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_room(self):
        form = BookingForm(data={
            "room": "",
            "check_in": "2026-07-01",
            "check_out": "2026-07-05",
            "guests": 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("room", form.errors)

    def test_form_widgets_have_form_control(self):
        form = BookingForm()
        for field in ["room", "check_in", "check_out", "guests"]:
            self.assertIn("form-control", form.fields[field].widget.attrs.get("class", ""))


class BookingCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
        )
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="double",
            price_per_night=150, capacity=2
        )

    def test_url_resolves_to_create_view(self):
        match = resolve("/bookings/create/")
        self.assertEqual(match.func.view_class, BookingCreateView)

    def test_login_required(self):
        response = self.client.get(reverse("bookings:booking_create"))
        self.assertRedirects(response, "/accounts/login/?next=/bookings/create/")

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("bookings:booking_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/booking_form.html")

    def test_booking_created_with_total_price(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("bookings:booking_create"), data={
            "room": self.room.id,
            "check_in": "2026-07-01",
            "check_out": "2026-07-05",
            "guests": 2,
        })
        self.assertRedirects(response, reverse("bookings:booking_list"))
        booking = Booking.objects.get(room=self.room)
        self.assertEqual(booking.user, self.user)
        self.assertEqual(booking.total_price, 600)
        self.assertEqual(booking.guests, 2)

    def test_booking_price_computed_as_nights_times_rate(self):
        self.client.force_login(self.user)
        self.client.post(reverse("bookings:booking_create"), data={
            "room": self.room.id,
            "check_in": "2026-07-01",
            "check_out": "2026-07-03",
            "guests": 1,
        })
        booking = Booking.objects.get(room=self.room)
        self.assertEqual(booking.total_price, 300)


class BookingListViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass"
        )
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="double",
            price_per_night=100, capacity=2
        )
        for _ in range(3):
            Booking.objects.create(
                user=self.user1, room=self.room,
                check_in=date(2026, 7, 1), check_out=date(2026, 7, 3),
                guests=1, total_price=200,
            )
        Booking.objects.create(
            user=self.user2, room=self.room,
            check_in=date(2026, 8, 1), check_out=date(2026, 8, 5),
            guests=2, total_price=400,
        )

    def test_url_resolves_to_list_view(self):
        match = resolve("/bookings/")
        self.assertEqual(match.func.view_class, BookingListView)

    def test_login_required(self):
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertRedirects(response, "/accounts/login/?next=/bookings/")

    def test_uses_correct_template(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertTemplateUsed(response, "bookings/booking_list.html")

    def test_only_user_bookings_shown(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(len(response.context["bookings"]), 3)
        for booking in response.context["bookings"]:
            self.assertEqual(booking.user, self.user1)

    def test_other_user_bookings_not_shown(self):
        self.client.force_login(self.user2)
        response = self.client.get(reverse("bookings:booking_list"))
        self.assertEqual(len(response.context["bookings"]), 1)
        self.assertEqual(response.context["bookings"][0].user, self.user2)

    def test_bookings_ordered_by_newest_first(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("bookings:booking_list"))
        bookings = list(response.context["bookings"])
        self.assertEqual(bookings, sorted(bookings, key=lambda b: b.created_at, reverse=True))


class BookingDetailViewTests(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass"
        )
        self.user2 = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass"
        )
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="double",
            price_per_night=100, capacity=2
        )
        self.booking = Booking.objects.create(
            user=self.user1, room=self.room,
            check_in=date(2026, 7, 1), check_out=date(2026, 7, 5),
            guests=2, total_price=400,
        )

    def test_url_resolves_to_detail_view(self):
        match = resolve(f"/bookings/{self.booking.id}/")
        self.assertEqual(match.func.view_class, BookingDetailView)

    def test_login_required(self):
        response = self.client.get(reverse("bookings:booking_detail", args=[self.booking.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/bookings/{self.booking.id}/")

    def test_uses_correct_template(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("bookings:booking_detail", args=[self.booking.id]))
        self.assertTemplateUsed(response, "bookings/booking_detail.html")

    def test_context_contains_booking(self):
        self.client.force_login(self.user1)
        response = self.client.get(reverse("bookings:booking_detail", args=[self.booking.id]))
        self.assertEqual(response.context["booking"], self.booking)

    def test_other_user_cannot_access(self):
        self.client.force_login(self.user2)
        response = self.client.get(reverse("bookings:booking_detail", args=[self.booking.id]))
        self.assertEqual(response.status_code, 404)
