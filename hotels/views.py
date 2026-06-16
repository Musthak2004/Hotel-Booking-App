from django.shortcuts import redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from reviews.models import Review
from .models import Hotel
from .forms import HotelForm


# LIST (public)
class HotelListView(ListView):
    model = Hotel
    template_name = "hotels/hotel_list.html"
    context_object_name = "hotels"
    paginate_by = 9

    def get_queryset(self):
        try:
            qs = Hotel.objects.filter(is_active=True)
            self._q = self.request.GET.get("q", "").strip()
            self._city = self.request.GET.get("city", "").strip()
            self._sort = self.request.GET.get("sort", "")
            if self._q:
                qs = qs.filter(name__icontains=self._q)
            if self._city:
                qs = qs.filter(city__iexact=self._city)
            if self._sort == "name":
                qs = qs.order_by("name")
            else:
                qs = qs.order_by("-created_at")
            return qs
        except Exception:
            return Hotel.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context["cities"] = (
                Hotel.objects.filter(is_active=True)
                .values_list("city", flat=True)
                .distinct()
                .order_by("city")
            )
        except Exception:
            context["cities"] = []
        context["current_q"] = self._q if hasattr(self, '_q') else ""
        context["current_city"] = self._city if hasattr(self, '_city') else ""
        context["current_sort"] = self._sort if hasattr(self, '_sort') else ""
        return context


# DETAIL (public)
class HotelDetailView(DetailView):
    model = Hotel
    template_name = "hotels/hotel_detail.html"
    context_object_name = "hotel"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        if user.is_authenticated:
            context["user_review"] = Review.objects.filter(
                hotel=self.object, user=user
            ).first()
        return context


# CREATE (owner only)
class HotelCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Hotel
    form_class = HotelForm
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:hotel_list")

    def test_func(self):
        return self.request.user.role == "owner"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only hotel owners can create listings.")
        return redirect("hotels:hotel_list")

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


# UPDATE (only owner)
class HotelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Hotel
    form_class = HotelForm
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:hotel_list")

    def test_func(self):
        hotel = self.get_object()
        return self.request.user == hotel.owner

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only edit your own hotels.")
        return redirect("hotels:hotel_list")


# DELETE (only owner)
class HotelDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Hotel
    template_name = "hotels/hotel_confirm_delete.html"
    success_url = reverse_lazy("hotels:hotel_list")

    def test_func(self):
        hotel = self.get_object()
        return self.request.user == hotel.owner

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only delete your own hotels.")
        return redirect("hotels:hotel_list")