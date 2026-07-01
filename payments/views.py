from django.contrib import messages
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from bookings.models import Booking
from .models import Payment
from .services import create_checkout_session


class PaymentCheckoutView(LoginRequiredMixin, View):
    """Create a Stripe Checkout Session and redirect the user to Stripe."""

    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        if booking.user != request.user:
            raise Http404

        # Already paid
        if hasattr(booking, "payment") and booking.payment.status == "completed":
            messages.info(request, "This booking is already paid.")
            return redirect("bookings:booking_detail", booking.id)

        # Create or get existing pending payment record
        payment, _ = Payment.objects.get_or_create(
            booking=booking,
            defaults={
                "amount": booking.total_price,
                "payment_method": "card",
                "status": "pending",
            },
        )

        try:
            session = create_checkout_session(booking, request)
        except Exception as e:
            messages.error(request, f"Could not initiate payment: {e}")
            return redirect("bookings:booking_detail", booking.id)

        # Store the Stripe session ID
        payment.stripe_session_id = session["id"]
        payment.transaction_id = session.get("payment_intent", "")
        payment.save(update_fields=["stripe_session_id", "transaction_id"])

        return redirect(session.url)


class PaymentSuccessView(LoginRequiredMixin, TemplateView):
    """Landing page after successful Stripe payment."""

    template_name = "payments/payment_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = get_object_or_404(
            Booking, id=self.kwargs["booking_id"], user=self.request.user
        )
        return context


class PaymentCancelledView(LoginRequiredMixin, TemplateView):
    """Landing page when the user cancels the Stripe payment."""

    template_name = "payments/payment_cancelled.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = get_object_or_404(
            Booking, id=self.kwargs["booking_id"], user=self.request.user
        )
        return context


class PaymentDetailView(LoginRequiredMixin, DetailView):
    model = Payment
    template_name = "payments/payment_detail.html"
    context_object_name = "payment"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.booking.user != self.request.user:
            raise Http404
        return obj
