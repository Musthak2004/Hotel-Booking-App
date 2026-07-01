from datetime import date, timedelta
from unittest.mock import patch
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from hotels.models import Hotel
from rooms.models import Room
from .models import Booking
from .forms import BookingForm
from .views import BookingCreateView, BookingListView, BookingDetailView, BookingCancelView

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

    def test_form_check_out_before_check_in(self):
        form = BookingForm(data={
            "room": self.room.id,
            "check_in": "2026-07-10",
            "check_out": "2026-07-05",
            "guests": 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("check_out", form.errors)
        self.assertIn("after check-in", str(form.errors["check_out"][0]).lower())

    def test_form_check_in_in_past(self):
        form = BookingForm(data={
            "room": self.room.id,
            "check_in": "2020-01-01",
            "check_out": "2020-01-05",
            "guests": 2,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("check_in", form.errors)
        self.assertIn("past", str(form.errors["check_in"][0]).lower())

    def test_form_guests_exceed_capacity(self):
        form = BookingForm(data={
            "room": self.room.id,
            "check_in": "2026-08-01",
            "check_out": "2026-08-05",
            "guests": 10,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("guests", form.errors)

    def test_overlap_rejected(self):
        # Create an existing booking
        Booking.objects.create(
            user=self.owner, room=self.room,
            check_in=date(2026, 8, 1), check_out=date(2026, 8, 5),
            guests=1, total_price=600,
        )
        # Try to create an overlapping one
        form = BookingForm(data={
            "room": self.room.id,
            "check_in": "2026-08-03",
            "check_out": "2026-08-07",
            "guests": 1,
        })
        self.assertFalse(form.is_valid())
        self.assertIn("already booked", str(form.errors["__all__"][0]).lower())

    def test_non_overlap_accepted(self):
        Booking.objects.create(
            user=self.owner, room=self.room,
            check_in=date(2026, 8, 1), check_out=date(2026, 8, 5),
            guests=1, total_price=600,
        )
        # Non-overlapping — starts after the existing booking ends
        form = BookingForm(data={
            "room": self.room.id,
            "check_in": "2026-08-06",
            "check_out": "2026-08-10",
            "guests": 1,
        })
        self.assertTrue(form.is_valid())

    def test_cancelled_does_not_block(self):
        Booking.objects.create(
            user=self.owner, room=self.room,
            check_in=date(2026, 8, 1), check_out=date(2026, 8, 5),
            guests=1, total_price=600, status="cancelled",
        )
        form = BookingForm(data={
            "room": self.room.id,
            "check_in": "2026-08-03",
            "check_out": "2026-08-07",
            "guests": 1,
        })
        self.assertTrue(form.is_valid())


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


class BookingMessageTests(TestCase):
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

    def test_success_message_on_booking_create(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("bookings:booking_create"), data={
            "room": self.room.id,
            "check_in": date.today() + timedelta(days=10),
            "check_out": date.today() + timedelta(days=13),
            "guests": 1,
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("created" in str(m).lower() for m in messages))


class BookingCancelViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user1@example.com", password="pass"
        )
        self.other_user = User.objects.create_user(
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
            price_per_night=150, capacity=2
        )
        self.booking = Booking.objects.create(
            user=self.user, room=self.room,
            check_in=date.today() + timedelta(days=3),
            check_out=date.today() + timedelta(days=6),
            guests=2, total_price=450,
        )
        self.cancel_url = reverse("bookings:booking_cancel", args=[self.booking.pk])

    def test_url_resolves(self):
        match = resolve(f"/bookings/{self.booking.pk}/cancel/")
        self.assertEqual(match.func.view_class, BookingCancelView)

    def test_cancel_pending_booking(self):
        self.client.force_login(self.user)
        response = self.client.post(self.cancel_url, follow=True)
        self.assertRedirects(
            response, reverse("bookings:booking_detail", args=[self.booking.pk])
        )
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "cancelled")

    def test_get_shows_confirmation_page(self):
        self.client.force_login(self.user)
        response = self.client.get(self.cancel_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "bookings/booking_confirm_cancel.html")
        self.assertEqual(response.context["booking"], self.booking)

    @patch("stripe.checkout.Session.retrieve")
    @patch("stripe.Refund.create")
    def test_cancel_confirmed_booking_with_payment_triggers_refund(
        self, mock_refund, mock_retrieve
    ):
        """Cancelling a confirmed (paid) booking calls Stripe refund."""
        from payments.models import Payment
        Payment.objects.create(
            booking=self.booking, amount=450, payment_method="card",
            status="completed",
            stripe_session_id="cs_test_123",
        )
        mock_session = {"id": "cs_test_123", "payment_intent": {"id": "pi_test_456"}}
        mock_retrieve.return_value = mock_session

        self.client.force_login(self.user)
        response = self.client.post(self.cancel_url, follow=True)
        self.assertRedirects(
            response, reverse("bookings:booking_detail", args=[self.booking.pk])
        )
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "cancelled")
        payment = self.booking.payment
        self.assertEqual(payment.status, "refunded")
        mock_retrieve.assert_called_once_with(
            "cs_test_123", expand=["payment_intent"]
        )
        mock_refund.assert_called_once_with(payment_intent="pi_test_456")

    def test_already_cancelled_does_not_change_status(self):
        self.booking.status = "cancelled"
        self.booking.save(update_fields=["status"])
        self.client.force_login(self.user)
        response = self.client.post(self.cancel_url, follow=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "cancelled")
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("already" in str(m).lower() for m in messages))

    def test_other_user_cannot_cancel(self):
        self.client.force_login(self.other_user)
        response = self.client.post(self.cancel_url, follow=True)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "pending")
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("own bookings" in str(m).lower() for m in messages))

    def test_login_required(self):
        response = self.client.post(self.cancel_url)
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/bookings/{self.booking.pk}/cancel/"
        )

    def test_success_message_on_cancel(self):
        self.client.force_login(self.user)
        response = self.client.post(self.cancel_url, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("cancelled" in str(m).lower() for m in messages))
