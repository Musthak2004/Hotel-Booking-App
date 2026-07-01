from datetime import date

from django.contrib import messages
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, DetailView, CreateView

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from rooms.models import Room
from .models import Booking
from .forms import BookingForm


class BookingCreateView(LoginRequiredMixin, CreateView):

    model = Booking
    form_class = BookingForm
    template_name = "bookings/booking_form.html"
    success_url = reverse_lazy("bookings:booking_list")

    def get_initial(self):
        initial = super().get_initial()
        room_id = self.request.GET.get("room")
        if room_id:
            try:
                room = Room.objects.get(pk=room_id)
                initial["room"] = room
            except Room.DoesNotExist:
                pass
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        room_id = self.request.GET.get("room")
        if room_id:
            room = get_object_or_404(Room, pk=room_id)
            context["selected_room"] = room
        return context

    @transaction.atomic
    def form_valid(self, form):
        form.instance.user = self.request.user

        # Lock the room row to prevent race conditions on availability
        room = Room.objects.select_for_update().get(
            pk=form.instance.room.pk
        )

        days = (
            form.instance.check_out -
            form.instance.check_in
        ).days

        # Check seasonal pricing rules
        from rooms.models import PriceRule
        price_rule = PriceRule.objects.filter(
            room=room,
            start_date__lt=form.instance.check_out,
            end_date__gt=form.instance.check_in,
        ).first()
        if price_rule:
            price_per_night = price_rule.price_per_night
        else:
            price_per_night = room.price_per_night

        form.instance.total_price = price_per_night * days

        # Check if promo code was provided
        promo_code = form.cleaned_data.get("promo_code", "")
        if promo_code:
            from bookings.models import PromoCode
            try:
                pc = PromoCode.objects.get(
                    code=promo_code, is_active=True,
                    valid_from__lte=date.today(),
                    valid_until__gte=date.today(),
                )
                if pc.max_uses == 0 or pc.used_count < pc.max_uses:
                    form.instance.total_price = pc.apply_discount(
                        form.instance.total_price
                    )
                    pc.used_count += 1
                    pc.save(update_fields=["used_count"])
                    messages.success(
                        self.request,
                        f"Promo code '{pc.code}' applied! "
                        f"{pc.discount_percent}% discount."
                    )
                else:
                    messages.warning(
                        self.request, "Promo code has expired."
                    )
            except PromoCode.DoesNotExist:
                messages.warning(
                    self.request, "Invalid promo code."
                )

        messages.success(self.request, "Booking created successfully!")

        # Send confirmation email
        try:
            from .emails import send_booking_confirmation
            send_booking_confirmation(form.instance)
        except Exception:
            pass

        return super().form_valid(form)


class BookingListView(LoginRequiredMixin, ListView):

    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):
        return Booking.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class BookingDetailView(LoginRequiredMixin, DetailView):

    model = Booking
    template_name = "bookings/booking_detail.html"
    context_object_name = "booking"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.user != self.request.user:
            raise Http404
        return obj


class BookingCancelView(LoginRequiredMixin, UserPassesTestMixin, DetailView):

    model = Booking
    template_name = "bookings/booking_confirm_cancel.html"
    context_object_name = "booking"

    def test_func(self):
        booking = self.get_object()
        return booking.user == self.request.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only cancel your own bookings.")
        return redirect("bookings:booking_list")

    def post(self, request, *args, **kwargs):
        booking = self.get_object()

        if booking.status in ("cancelled", "completed"):
            messages.info(
                request,
                f"This booking is already {booking.status}."
            )
            return redirect("bookings:booking_detail", pk=booking.pk)

        booking.status = "cancelled"

        # If the booking was paid, attempt a Stripe refund
        payment = getattr(booking, "payment", None)
        if payment and payment.status == "completed" and payment.stripe_session_id:
            try:
                import stripe
                from django.conf import settings
                stripe.api_key = settings.STRIPE_SECRET_KEY
                # Retrieve the session to get the payment intent ID
                session = stripe.checkout.Session.retrieve(
                    payment.stripe_session_id,
                    expand=["payment_intent"]
                )
                payment_intent = session.get("payment_intent")
                if payment_intent and payment_intent.get("id"):
                    stripe.Refund.create(
                        payment_intent=payment_intent["id"]
                    )
                    payment.status = "refunded"
                    payment.save(update_fields=["status"])
                    messages.success(
                        request,
                        "Booking cancelled and payment refunded."
                    )
                else:
                    messages.warning(
                        request,
                        "Booking cancelled. Unable to process refund "
                        "(no payment intent found)."
                    )
            except Exception as e:
                messages.warning(
                    request,
                    f"Booking cancelled. Refund failed: {e}"
                )
        elif payment and payment.status == "completed":
            payment.status = "refunded"
            payment.save(update_fields=["status"])
            messages.success(request, "Booking cancelled and payment refunded.")

        booking.save(update_fields=["status"])

        # Send cancellation email
        try:
            from .emails import send_booking_cancellation
            send_booking_cancellation(booking)
        except Exception:
            pass

        messages.success(request, "Booking cancelled successfully!")
        return redirect("bookings:booking_detail", pk=booking.pk)
