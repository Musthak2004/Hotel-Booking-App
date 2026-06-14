from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages

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

        if self._q:
            from django.db.models import Q
            qs = qs.filter(
                Q(room_number__icontains=self._q) |
                Q(hotel__name__icontains=self._q)
            )
        if self._hotel:
            qs = qs.filter(hotel_id=self._hotel)
        if self._room_type:
            qs = qs.filter(room_type=self._room_type)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_q"] = self._q
        context["current_hotel"] = self._hotel
        context["current_room_type"] = self._room_type
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

    def test_func(self):
        room = self.get_object()
        return self.request.user == room.hotel.owner

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only delete rooms in your own hotels.")
        return redirect("rooms:room_list")
