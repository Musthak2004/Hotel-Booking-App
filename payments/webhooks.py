from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

import stripe

from bookings.models import Booking
from .models import Payment

stripe.api_key = settings.STRIPE_SECRET_KEY


@require_POST
@csrf_exempt
def stripe_webhook(request):
    """Handle incoming Stripe webhook events."""
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")

    if not settings.STRIPE_WEBHOOK_SECRET:
        return HttpResponse("Webhook secret not configured", status=500)

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except (ValueError, stripe.error.SignatureVerificationError):
        return HttpResponse(status=400)

    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        booking_id = session["metadata"]["booking_id"]

        try:
            booking = Booking.objects.get(id=booking_id)
        except Booking.DoesNotExist:
            return HttpResponse(status=404)

        payment, created = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                "amount": booking.total_price,
                "payment_method": "card",
                "transaction_id": session.get("payment_intent", ""),
                "stripe_session_id": session["id"],
                "status": "completed",
                "paid_at": timezone.now(),
            },
        )
        if not created:
            payment.status = "completed"
            payment.transaction_id = session.get("payment_intent", "")
            payment.stripe_session_id = session["id"]
            payment.paid_at = timezone.now()
            payment.save()

        booking.status = "confirmed"
        booking.save(update_fields=["status"])

        # Send payment receipt email
        try:
            from .emails import send_payment_receipt
            send_payment_receipt(payment)
        except Exception:
            pass

        # Send booking confirmation email
        try:
            from bookings.emails import send_booking_confirmation
            send_booking_confirmation(booking)
        except Exception:
            pass

    return HttpResponse(status=200)
