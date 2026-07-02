from datetime import date, timedelta
from unittest.mock import patch, MagicMock
from django.test import TestCase, override_settings
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from hotels.models import Hotel
from rooms.models import Room
from bookings.models import Booking
from .models import Payment
from .forms import PaymentForm
from .views import PaymentCheckoutView, PaymentDetailView, PaymentSuccessView, PaymentCancelledView

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
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=5),
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

    def test_stripe_session_id_field(self):
        payment = Payment.objects.create(
            booking=self.booking, amount=600, payment_method="card",
            stripe_session_id="cs_test_abc123",
        )
        self.assertEqual(payment.stripe_session_id, "cs_test_abc123")


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


class PaymentCheckoutViewTests(TestCase):
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
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=5),
            guests=2, total_price=600,
        )

    def test_url_resolves_to_checkout_view(self):
        match = resolve(f"/payments/checkout/{self.booking.id}/")
        self.assertEqual(match.func.view_class, PaymentCheckoutView)

    def test_login_required(self):
        response = self.client.get(
            reverse("payments:payment_checkout", args=[self.booking.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/payments/checkout/{self.booking.id}/"
        )

    def test_other_user_cannot_access_booking(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("payments:payment_checkout", args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 404)

    @patch("payments.views.create_checkout_session")
    def test_redirects_to_stripe(self, mock_create_checkout):
        mock_session = MagicMock()
        mock_session.url = "https://checkout.stripe.com/test"
        mock_session.__getitem__ = lambda self, key: "cs_test_abc"
        mock_session.get = lambda key, default="": "pi_test_xyz"
        mock_create_checkout.return_value = mock_session

        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_checkout", args=[self.booking.id])
        )
        self.assertRedirects(response, "https://checkout.stripe.com/test", fetch_redirect_response=False)
        self.assertTrue(Payment.objects.filter(booking=self.booking).exists())

    def test_redirects_if_payment_already_completed(self):
        Payment.objects.create(
            booking=self.booking, amount=600, payment_method="card",
            status="completed"
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_checkout", args=[self.booking.id])
        )
        self.assertRedirects(
            response,
            reverse("bookings:booking_detail", args=[self.booking.id])
        )

    def test_404_for_non_existent_booking(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_checkout", args=[999])
        )
        self.assertEqual(response.status_code, 404)


class PaymentSuccessViewTests(TestCase):
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
        self.booking = Booking.objects.create(
            user=self.user, room=self.room,
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=5),
            guests=2, total_price=600,
        )

    def test_url_resolves(self):
        match = resolve(f"/payments/success/{self.booking.id}/")
        self.assertEqual(match.func.view_class, PaymentSuccessView)

    def test_login_required(self):
        response = self.client.get(
            reverse("payments:payment_success", args=[self.booking.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/payments/success/{self.booking.id}/"
        )

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_success", args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/payment_success.html")

    def test_context_contains_booking(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_success", args=[self.booking.id])
        )
        self.assertEqual(response.context["booking"], self.booking)


class PaymentCancelledViewTests(TestCase):
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
        self.booking = Booking.objects.create(
            user=self.user, room=self.room,
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=5),
            guests=2, total_price=600,
        )

    def test_url_resolves(self):
        match = resolve(f"/payments/cancelled/{self.booking.id}/")
        self.assertEqual(match.func.view_class, PaymentCancelledView)

    def test_login_required(self):
        response = self.client.get(
            reverse("payments:payment_cancelled", args=[self.booking.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/payments/cancelled/{self.booking.id}/"
        )

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_cancelled", args=[self.booking.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payments/payment_cancelled.html")

    def test_context_contains_booking(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("payments:payment_cancelled", args=[self.booking.id])
        )
        self.assertEqual(response.context["booking"], self.booking)


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
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=5),
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


class FakeStripeError(Exception):
    """Fake base for stripe.error.StripeError (stripe not installed locally)."""
    pass


class FakeSignatureVerificationError(FakeStripeError):
    """Fake stripe.error.SignatureVerificationError."""
    pass


def _mock_stripe():
    """Return a MagicMock configured as a fake stripe module."""
    sm = MagicMock()
    sm.Webhook.construct_event.return_value = MagicMock()
    sm.error.SignatureVerificationError = FakeSignatureVerificationError
    return sm


@override_settings(STRIPE_WEBHOOK_SECRET="whsec_test")
class StripeWebhookTests(TestCase):
    """Tests for the Stripe webhook endpoint."""

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
            check_in=date.today() + timedelta(days=1),
            check_out=date.today() + timedelta(days=5),
            guests=2, total_price=600,
        )
        self.webhook_url = reverse("payments:stripe_webhook")

    @patch("payments.webhooks._get_stripe")
    def test_valid_checkout_session_creates_payment_and_confirms_booking(self, mock_get_stripe):
        """A valid checkout.session.completed event creates a Payment
        and sets booking.status = 'confirmed'."""
        stripe_mock = _mock_stripe()
        mock_get_stripe.return_value = stripe_mock
        stripe_mock.Webhook.construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_valid123",
                    "metadata": {"booking_id": str(self.booking.id)},
                    "payment_intent": "pi_test_valid",
                }
            },
        }
        response = self.client.post(
            self.webhook_url,
            data='{"dummy":"payload"}',
            content_type="application/json",
            HTTP_STRIPE_SIGNATURE="test_sig",
        )
        self.assertEqual(response.status_code, 200)
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "confirmed")
        payment = Payment.objects.get(booking=self.booking)
        self.assertEqual(payment.status, "completed")
        self.assertEqual(payment.stripe_session_id, "cs_test_valid123")
        self.assertEqual(payment.transaction_id, "pi_test_valid")
        self.assertEqual(payment.amount, 600)

    @patch("payments.webhooks._get_stripe")
    def test_duplicate_webhook_is_idempotent(self, mock_get_stripe):
        """A second webhook with the same session ID should not error."""
        stripe_mock = _mock_stripe()
        mock_get_stripe.return_value = stripe_mock
        event_data = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_dup",
                    "metadata": {"booking_id": str(self.booking.id)},
                    "payment_intent": "pi_test_dup",
                }
            },
        }
        stripe_mock.Webhook.construct_event.return_value = event_data

        # First call
        self.client.post(
            self.webhook_url,
            data='{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(Payment.objects.filter(booking=self.booking).count(), 1)

        # Second call (duplicate)
        stripe_mock.Webhook.construct_event.return_value = event_data
        response2 = self.client.post(
            self.webhook_url,
            data='{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(response2.status_code, 200)
        # Still only one payment record
        self.assertEqual(Payment.objects.filter(booking=self.booking).count(), 1)
        # Booking stays confirmed
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "confirmed")

    @patch("payments.webhooks._get_stripe")
    def test_invalid_signature_returns_400(self, mock_get_stripe):
        """When construct_event raises SignatureVerificationError,
        the endpoint returns 400."""
        stripe_mock = _mock_stripe()
        mock_get_stripe.return_value = stripe_mock
        stripe_mock.Webhook.construct_event.side_effect = FakeSignatureVerificationError(
            "Invalid signature", None
        )
        response = self.client.post(
            self.webhook_url,
            data='{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="bad_sig",
        )
        self.assertEqual(response.status_code, 400)

    @patch("payments.webhooks._get_stripe")
    def test_invalid_payload_returns_400(self, mock_get_stripe):
        """When construct_event raises ValueError, the endpoint returns 400."""
        stripe_mock = _mock_stripe()
        mock_get_stripe.return_value = stripe_mock
        stripe_mock.Webhook.construct_event.side_effect = ValueError("Invalid payload")
        response = self.client.post(
            self.webhook_url,
            data='garbage', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(response.status_code, 400)

    def test_missing_webhook_secret_returns_500(self):
        """When STRIPE_WEBHOOK_SECRET is empty, the endpoint returns 500."""
        with self.settings(STRIPE_WEBHOOK_SECRET=""):
            response = self.client.post(
                self.webhook_url,
                data='{}', content_type="application/json",
                HTTP_STRIPE_SIGNATURE="sig",
            )
        self.assertEqual(response.status_code, 500)
        self.assertIn(b"not configured", response.content)

    @patch("payments.webhooks._get_stripe")
    def test_unknown_booking_id_returns_404(self, mock_get_stripe):
        """A checkout.session.completed event with a non-existent
        booking_id returns 404."""
        stripe_mock = _mock_stripe()
        mock_get_stripe.return_value = stripe_mock
        stripe_mock.Webhook.construct_event.return_value = {
            "type": "checkout.session.completed",
            "data": {
                "object": {
                    "id": "cs_test_unknown",
                    "metadata": {"booking_id": "9999"},
                    "payment_intent": "pi_test_unknown",
                }
            },
        }
        response = self.client.post(
            self.webhook_url,
            data='{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(response.status_code, 404)

    @patch("payments.webhooks._get_stripe")
    def test_unhandled_event_type_returns_200(self, mock_get_stripe):
        """An event type that is not handled returns 200 and is
        silently ignored."""
        stripe_mock = _mock_stripe()
        mock_get_stripe.return_value = stripe_mock
        stripe_mock.Webhook.construct_event.return_value = {
            "type": "payment_intent.succeeded",
            "data": {"object": {"id": "pi_test_unhandled"}},
        }
        response = self.client.post(
            self.webhook_url,
            data='{}', content_type="application/json",
            HTTP_STRIPE_SIGNATURE="sig",
        )
        self.assertEqual(response.status_code, 200)
