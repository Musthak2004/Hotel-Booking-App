from datetime import date

from django.http import Http404
from django.urls import reverse_lazy

from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
)

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Booking
from .forms import BookingForm

class BookingCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = Booking

    form_class = BookingForm

    template_name = (
        "bookings/booking_form.html"
    )

    success_url = reverse_lazy(
        "bookings:booking_list"
    )

    def form_valid(self, form):

        form.instance.user = self.request.user

        room = form.instance.room

        days = (
            form.instance.check_out -
            form.instance.check_in
        ).days

        form.instance.total_price = (
            room.price_per_night * days
        )

        return super().form_valid(form)
    
class BookingListView(
    LoginRequiredMixin,
    ListView
):

    model = Booking
    template_name = "bookings/booking_list.html"
    context_object_name = "bookings"
    paginate_by = 10

    def get_queryset(self):

        return Booking.objects.filter(
            user=self.request.user
        ).order_by("-created_at")
    
class BookingDetailView(
    LoginRequiredMixin,
    DetailView
):

    model = Booking

    template_name = (
        "bookings/booking_detail.html"
    )

    context_object_name = "booking"

    def get_object(self, queryset=None):
        obj = super().get_object(queryset=queryset)
        if obj.user != self.request.user:
            raise Http404
        return obj

