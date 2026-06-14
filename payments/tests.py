from datetime import date
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from hotels.models import Hotel
from rooms.models import Room
from bookings.models import Booking
from .models import Payment
from .forms import PaymentForm
from .views import PaymentCreateView, PaymentDetailView

User = get_user_model()


class PaymentModelTests(TestCase):
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
        self.booking = Booking.objects.create(
            user=self.user, room=self.room,
            check_in=date(2026, 7, 1), check_out=date(2026, 7, 5),
            guests=2, total_price=600,
        )

    def test_create_payment(self):
        payment = Payment.objects.create(
            booking=self.booking,
            amount=600,
            payment_method="card",
        )
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, 600)
        self.assertEqual(payment.payment_method, "card")
        self.assertEqual(payment.status, "pending")
        self.assertEqual(payment.transaction_id, "")

    def test_string_representation(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=600, payment_method="card"
        )
        self.assertIn(str(payment.id), str(payment))

    def test_default_status_pending(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=600, payment_method="card"
        )
        self.assertEqual(payment.status, "pending")

    def test_one_to_one_relationship(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=600, payment_method="card"
        )
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(self.booking.payment, payment)


class PaymentFormTests(TestCase):
    def test_form_valid_data(self):
        form = PaymentForm(data={
            "payment_method": "card",
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_payment_method(self):
        form = PaymentForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn("payment_method", form.errors)

    def test_form_widget_has_form_control(self):
        form = PaymentForm()
        self.assertIn("form-control", form.fields["payment_method"].widget.attrs.get("class", ""))


class PaymentCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
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
            check_in=date(2026, 7, 1), check_out=date(2026, 7, 5),
            guests=2, total_price=600,
        )

    def test_url_resolves_to_create_view(self):
        match = resolve(f"/payments/create/{self.booking.id}/")
        self.assertEqual(match.func.view_class, PaymentCreateView)

    def test_login_required(self):
        response = self.client.get(
            reverse("payments:payment_create", args=[self.booking.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/payments/create/{self.booking.id}/"
        )

    def test_other_user_cannot_access_booking(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("payments:payment_create", args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_create", args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/payment_form.html")

    def test_context_contains_booking(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_create", args=[self.booking.id])
        )
        self.assertEqual(response.context["booking"], self.booking)

    def test_redirects_if_payment_already_exists(self):
        Payment.objects.create(
            booking=self.booking, amount=600, payment_method="card"
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_create", args=[self.booking.id])
        )
        self.assertRedirects(
            response,
            reverse("bookings:booking_detail", args=[self.booking.id])
        )

    def test_creates_payment_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("payments:payment_create", args=[self.booking.id]),
            data={"payment_method": "card"},
        )
        self.assertRedirects(response, reverse("bookings:booking_list"))
        payment = Payment.objects.get(booking=self.booking)
        self.assertEqual(payment.amount, 600)
        self.assertEqual(payment.payment_method, "card")

    def test_amount_auto_set_from_booking_total_price(self):
        self.client.force_login(self.user)
        self.client.post(
            reverse("payments:payment_create", args=[self.booking.id]),
            data={"payment_method": "paypal"},
        )
        payment = Payment.objects.get(booking=self.booking)
        self.assertEqual(payment.amount, self.booking.total_price)

    def test_404_for_non_existent_booking(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_create", args=[999])
        )
        self.assertEqual(response.status_code, 404)


class PaymentDetailViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
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
            check_in=date(2026, 7, 1), check_out=date(2026, 7, 5),
            guests=2, total_price=600,
        )
        self.payment = Payment.objects.create(
            booking=self.booking, amount=600, payment_method="card"
        )

    def test_url_resolves_to_detail_view(self):
        match = resolve(f"/payments/{self.payment.id}/")
        self.assertEqual(match.func.view_class, PaymentDetailView)

    def test_login_required(self):
        response = self.client.get(
            reverse("payments:payment_detail", args=[self.payment.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/payments/{self.payment.id}/"
        )

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_detail", args=[self.payment.id])
        )
        self.assertTemplateUsed(response, "payments/payment_detail.html")

    def test_context_contains_payment(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_detail", args=[self.payment.id])
        )
        self.assertEqual(response.context["payment"], self.payment)

    def test_other_user_cannot_access(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("payments:payment_detail", args=[self.payment.id])
        )
        self.assertEqual(response.status_code, 404)

    def test_404_for_non_existent_payment(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("payments:payment_detail", args=[999]))
        self.assertEqual(response.status_code, 404)
