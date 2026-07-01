"""Email notification helpers for payments."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse


def send_payment_receipt(payment):
    """Send payment receipt to the customer."""
    booking = payment.booking
    customer_email = booking.user.email
    payment_url = (
        f"{settings.SITE_URL}{reverse('payments:payment_detail', args=[payment.pk])}"
        if hasattr(settings, "SITE_URL") and settings.SITE_URL
        else f"http://127.0.0.1:8000{reverse('payments:payment_detail', args=[payment.pk])}"
    )

    context = {
        "payment": payment,
        "booking": booking,
        "payment_url": payment_url,
        "customer_name": booking.user.get_full_name() or booking.user.username,
        "hotel_name": booking.room.hotel.name,
        "amount": payment.amount,
        "transaction_id": payment.transaction_id,
        "paid_at": payment.paid_at,
    }
    subject = f"Payment Receipt — Booking #{booking.id}"
    html_message = render_to_string("emails/payment_receipt.html", context)
    plain_message = render_to_string("emails/payment_receipt.txt", context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        html_message=html_message,
        fail_silently=True,
    )
