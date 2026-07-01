"""Email notification helpers for bookings."""

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.urls import reverse


def send_booking_confirmation(booking):
    """Send booking confirmation email to the customer and hotel owner."""
    customer_email = booking.user.email
    owner_email = booking.room.hotel.owner.email
    booking_url = (
        f"{settings.SITE_URL}{reverse('bookings:booking_detail', args=[booking.pk])}"
        if hasattr(settings, "SITE_URL") and settings.SITE_URL
        else f"http://127.0.0.1:8000{reverse('bookings:booking_detail', args=[booking.pk])}"
    )

    context = {
        "booking": booking,
        "booking_url": booking_url,
        "customer_name": booking.user.get_full_name() or booking.user.username,
        "hotel_name": booking.room.hotel.name,
        "room_number": booking.room.room_number,
        "check_in": booking.check_in,
        "check_out": booking.check_out,
        "guests": booking.guests,
        "total_price": booking.total_price,
    }
    subject = f"Booking Confirmed — {booking.room.hotel.name}"
    html_message = render_to_string("emails/booking_confirmation.html", context)
    plain_message = render_to_string("emails/booking_confirmation.txt", context)

    # Send to customer
    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        html_message=html_message,
        fail_silently=True,
    )

    # Send to hotel owner
    subject_owner = f"New Booking — {booking.room.hotel.name} (Booking #{booking.id})"
    send_mail(
        subject=subject_owner,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[owner_email],
        html_message=html_message,
        fail_silently=True,
    )


def send_booking_cancellation(booking):
    """Send cancellation notification to the customer."""
    customer_email = booking.user.email
    booking_url = (
        f"{settings.SITE_URL}{reverse('bookings:booking_detail', args=[booking.pk])}"
        if hasattr(settings, "SITE_URL") and settings.SITE_URL
        else f"http://127.0.0.1:8000{reverse('bookings:booking_detail', args=[booking.pk])}"
    )

    context = {
        "booking": booking,
        "booking_url": booking_url,
        "customer_name": booking.user.get_full_name() or booking.user.username,
        "hotel_name": booking.room.hotel.name,
    }
    subject = f"Booking Cancelled — {booking.room.hotel.name}"
    html_message = render_to_string("emails/booking_cancellation.html", context)
    plain_message = render_to_string("emails/booking_cancellation.txt", context)

    send_mail(
        subject=subject,
        message=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[customer_email],
        html_message=html_message,
        fail_silently=True,
    )
