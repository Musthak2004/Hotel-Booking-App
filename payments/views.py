from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
)
from django.contrib.auth.mixins import LoginRequiredMixin

from bookings.models import Booking
from .models import Payment
from .forms import PaymentForm

class PaymentCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = Payment

    form_class = PaymentForm

    template_name = (
        "payments/payment_form.html"
    )

    success_url = reverse_lazy(
        "bookings:booking_list"
    )

    def dispatch(self, *args, **kwargs):
        self.booking = get_object_or_404(
            Booking, id=self.kwargs["booking_id"]
        )
        if not self.request.user.is_authenticated:
            return super().dispatch(*args, **kwargs)
        if self.booking.user != self.request.user:
            raise Http404
        if hasattr(self.booking, "payment"):
            return redirect("bookings:booking_detail", self.booking.id)
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["booking"] = self.booking
        return context

    def form_valid(self, form):
        form.instance.booking = self.booking
        form.instance.amount = self.booking.total_price
        return super().form_valid(form)

class PaymentDetailView(
    LoginRequiredMixin,
    DetailView
):

    model = Payment

    template_name = (
        "payments/payment_detail.html"
    )

    context_object_name = "payment"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.booking.user != self.request.user:
            raise Http404
        return obj