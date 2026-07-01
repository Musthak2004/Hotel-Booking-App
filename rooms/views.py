from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, F

from .models import Room
from .forms import RoomForm


class RoomListView(ListView):
    model = Room
    template_name = "rooms/room_list.html"
    context_object_name = "rooms"
    paginate_by = 12

    def get_queryset(self):
        qs = Room.objects.filter(is_available=True)
        self._q = self.request.GET.get("q", "").strip()
        self._hotel = self.request.GET.get("hotel", "").strip()
        self._room_type = self.request.GET.get("room_type", "").strip()
        self._min_price = self.request.GET.get("min_price", "").strip()
        self._max_price = self.request.GET.get("max_price", "").strip()
        self._capacity = self.request.GET.get("capacity", "").strip()
        self._check_in = self.request.GET.get("check_in", "").strip()
        self._check_out = self.request.GET.get("check_out", "").strip()

        if self._q:
            qs = qs.filter(
                Q(room_number__icontains=self._q) |
                Q(hotel__name__icontains=self._q)
            )
        if self._hotel:
            qs = qs.filter(hotel_id=self._hotel)
        if self._room_type:
            qs = qs.filter(room_type=self._room_type)
        if self._min_price:
            try:
                qs = qs.filter(price_per_night__gte=float(self._min_price))
            except ValueError:
                pass
        if self._max_price:
            try:
                qs = qs.filter(price_per_night__lte=float(self._max_price))
            except ValueError:
                pass
        if self._capacity:
            try:
                qs = qs.filter(capacity__gte=int(self._capacity))
            except ValueError:
                pass

        # Date availability filter
        if self._check_in and self._check_out:
            try:
                from datetime import date
                ci = date.fromisoformat(self._check_in)
                co = date.fromisoformat(self._check_out)
                if co > ci:
                    # Filter to rooms with available count > 0 for the date range
                    from bookings.models import Booking
                    from django.db.models import Count, Subquery, OuterRef, IntegerField, Value
                    from django.db.models.functions import Coalesce

                    booked = Booking.objects.filter(
                        room=OuterRef("pk"),
                        status__in=("pending", "confirmed"),
                        check_in__lt=co,
                        check_out__gt=ci,
                    ).order_by().values("room").annotate(cnt=Count("pk")).values("cnt")

                    qs = qs.annotate(
                        _booked=Coalesce(
                            Subquery(booked, output_field=IntegerField()),
                            Value(0)
                        )
                    ).filter(total_rooms__gt=F("_booked"))
            except ValueError:
                pass

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_q"] = self._q if hasattr(self, '_q') else ""
        context["current_hotel"] = self._hotel if hasattr(self, '_hotel') else ""
        context["current_room_type"] = self._room_type if hasattr(self, '_room_type') else ""
        context["min_price"] = self._min_price if hasattr(self, '_min_price') else ""
        context["max_price"] = self._max_price if hasattr(self, '_max_price') else ""
        context["capacity"] = self._capacity if hasattr(self, '_capacity') else ""
        context["check_in"] = self._check_in if hasattr(self, '_check_in') else ""
        context["check_out"] = self._check_out if hasattr(self, '_check_out') else ""
        return context


class RoomDetailView(DetailView):
    model = Room
    template_name = "rooms/room_detail.html"
    context_object_name = "room"


class RoomCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Room
    form_class = RoomForm
    template_name = "rooms/room_form.html"
    success_url = reverse_lazy("rooms:room_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Room created successfully!")
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.role == "owner"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only hotel owners can create rooms.")
        return redirect("rooms:room_list")


class RoomUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Room
    form_class = RoomForm
    template_name = "rooms/room_form.html"
    success_url = reverse_lazy("rooms:room_list")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        messages.success(self.request, "Room updated successfully!")
        return super().form_valid(form)

    def test_func(self):
        room = self.get_object()
        return self.request.user == room.hotel.owner

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only edit rooms in your own hotels.")
        return redirect("rooms:room_list")


class RoomDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Room
    template_name = "rooms/room_confirm_delete.html"
    success_url = reverse_lazy("rooms:room_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from bookings.models import Booking
        context["bookings_count"] = Booking.objects.filter(room=self.object).count()
        return context

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Room deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        room = self.get_object()
        return self.request.user == room.hotel.owner

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only delete rooms in your own hotels.")
        return redirect("rooms:room_list")
