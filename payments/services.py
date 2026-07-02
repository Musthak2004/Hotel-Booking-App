from django.conf import settings
from django.urls import reverse


def _get_stripe():
    """Lazy-load stripe so a missing package doesn't crash unrelated pages."""
    try:
        import stripe as _s
        _s.api_key = settings.STRIPE_SECRET_KEY
        return _s
    except ImportError:
        return None


def create_checkout_session(booking, request):
    """Create a Stripe Checkout Session for the given booking."""
    stripe = _get_stripe()
    if stripe is None:
        raise ImportError(
            "Stripe package is not installed. "
            "Install it with: pip install stripe"
        )

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": f"Booking #{booking.id} — {booking.room.hotel.name}",
                        "description": (
                            f"Room {booking.room.room_number} | "
                            f"{booking.check_in} to {booking.check_out} | "
                            f"{booking.guests} guest(s)"
                        ),
                    },
                    "unit_amount": int(booking.total_price * 100),  # cents
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=request.build_absolute_uri(
            reverse("payments:payment_success", kwargs={"booking_id": booking.id})
        ),
        cancel_url=request.build_absolute_uri(
            reverse("payments:payment_cancelled", kwargs={"booking_id": booking.id})
        ),
        metadata={
            "booking_id": str(booking.id),
        },
    )
    return session
