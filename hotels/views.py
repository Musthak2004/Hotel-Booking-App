from datetime import date

from django.shortcuts import redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Exists, OuterRef, F, Value, IntegerField, Count, Subquery, Sum
from django.db.models.functions import Coalesce

from reviews.models import Review
from rooms.models import Room
from bookings.models import Booking
from payments.models import Payment
from .models import Hotel, Amenity
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
            self._country = self.request.GET.get("country", "").strip()
            self._check_in = self.request.GET.get("check_in", "").strip()
            self._check_out = self.request.GET.get("check_out", "").strip()
            self._guests = self.request.GET.get("guests", "").strip()
            self._min_price = self.request.GET.get("min_price", "").strip()
            self._max_price = self.request.GET.get("max_price", "").strip()
            self._sort = self.request.GET.get("sort", "")
            self._amenity = self.request.GET.get("amenity", "").strip()

            # Text search across name, city, country
            if self._q:
                qs = qs.filter(
                    Q(name__icontains=self._q) |
                    Q(city__icontains=self._q) |
                    Q(country__icontains=self._q)
                )

            # City filter
            if self._city:
                qs = qs.filter(city__iexact=self._city)

            # Country filter
            if self._country:
                qs = qs.filter(country__icontains=self._country)

            # Amenity filter
            if self._amenity:
                try:
                    qs = qs.filter(amenities__id=int(self._amenity))
                except ValueError:
                    pass

            # Room-level filters: only apply Exists subquery when at least one filter
            # that depends on rooms is active (price, guests, dates).
            has_room_filter = any([
                self._min_price, self._max_price, self._guests,
                self._check_in, self._check_out,
            ])

            if has_room_filter:
                room_qs = Room.objects.filter(hotel=OuterRef("pk"), is_available=True)

                if self._min_price:
                    try:
                        room_qs = room_qs.filter(price_per_night__gte=float(self._min_price))
                    except ValueError:
                        pass
                if self._max_price:
                    try:
                        room_qs = room_qs.filter(price_per_night__lte=float(self._max_price))
                    except ValueError:
                        pass

                if self._guests:
                    try:
                        room_qs = room_qs.filter(capacity__gte=int(self._guests))
                    except ValueError:
                        pass

                if self._check_in and self._check_out:
                    try:
                        ci = date.fromisoformat(self._check_in)
                        co = date.fromisoformat(self._check_out)
                        if co > ci:
                            booking_count = Booking.objects.filter(
                                room=OuterRef("pk"),
                                status__in=("pending", "confirmed"),
                                check_in__lt=co,
                                check_out__gt=ci,
                            ).order_by().values("room").annotate(cnt=Count("pk")).values("cnt")

                            room_qs = room_qs.annotate(
                                _booked=Coalesce(
                                    Subquery(booking_count, output_field=IntegerField()),
                                    Value(0)
                                )
                            ).filter(total_rooms__gt=F("_booked"))
                    except ValueError:
                        pass

                qs = qs.filter(Exists(room_qs))

            # Sorting
            if self._sort == "name":
                qs = qs.order_by("name")
            else:
                qs = qs.order_by("-created_at")

            return qs.distinct()
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
        context["check_in"] = self._check_in if hasattr(self, '_check_in') else ""
        context["check_out"] = self._check_out if hasattr(self, '_check_out') else ""
        context["guests"] = self._guests if hasattr(self, '_guests') else ""
        context["min_price"] = self._min_price if hasattr(self, '_min_price') else ""
        context["max_price"] = self._max_price if hasattr(self, '_max_price') else ""
        context["country"] = self._country if hasattr(self, '_country') else ""
        context["current_amenity"] = self._amenity if hasattr(self, '_amenity') else ""
        try:
            context["all_amenities"] = Amenity.objects.all()
        except Exception:
            context["all_amenities"] = []
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
            context["has_saved"] = user.saved_hotels.filter(
                pk=self.object.pk
            ).exists()
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
        messages.success(self.request, "Hotel created successfully!")
        return super().form_valid(form)


# UPDATE (only owner)
class HotelUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Hotel
    form_class = HotelForm
    template_name = "hotels/hotel_form.html"
    success_url = reverse_lazy("hotels:hotel_list")

    def form_valid(self, form):
        messages.success(self.request, "Hotel updated successfully!")
        return super().form_valid(form)

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        hotel = self.object
        context["rooms_count"] = hotel.rooms.count()
        context["bookings_count"] = Booking.objects.filter(room__hotel=hotel).count()
        context["reviews_count"] = Review.objects.filter(hotel=hotel).count()
        return context

    def test_func(self):
        hotel = self.get_object()
        return self.request.user == hotel.owner

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "You can only delete your own hotels.")
        return redirect("hotels:hotel_list")

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Hotel deleted successfully!")
        return super().delete(request, *args, **kwargs)


class OwnerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    """Dashboard for hotel owners showing bookings, revenue, and occupancy stats."""

    template_name = "hotels/owner_dashboard.html"

    def test_func(self):
        return self.request.user.role == "owner"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(self.request, "Only hotel owners can access the dashboard.")
        return redirect("home")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        hotels = Hotel.objects.filter(owner=user)
        context["hotels"] = hotels

        # Aggregate booking IDs for this owner's hotels
        bookings_qs = Booking.objects.filter(room__hotel__owner=user)

        # Stats
        total_bookings = bookings_qs.count()
        active_bookings = bookings_qs.filter(
            status__in=("pending", "confirmed")
        ).count()

        # Revenue from completed payments
        revenue = Payment.objects.filter(
            booking__room__hotel__owner=user,
            status="completed",
        ).aggregate(total=Coalesce(Sum("amount"), Value(0)))["total"]

        context["stats"] = {
            "total_hotels": hotels.count(),
            "total_rooms": Room.objects.filter(hotel__owner=user).count(),
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "revenue": revenue,
        }

        # Recent bookings across all hotels
        context["recent_bookings"] = bookings_qs.select_related(
            "user", "room__hotel"
        ).order_by("-created_at")[:10]

        # Per-hotel summary
        hotel_stats = []
        for hotel in hotels:
            hotel_bookings = Booking.objects.filter(room__hotel=hotel)
            hotel_payments = Payment.objects.filter(
                booking__room__hotel=hotel, status="completed"
            )
            hotel_stats.append({
                "hotel": hotel,
                "room_count": hotel.rooms.count(),
                "booking_count": hotel_bookings.count(),
                "active_booking_count": hotel_bookings.filter(
                    status__in=("pending", "confirmed")
                ).count(),
                "revenue": hotel_payments.aggregate(
                    total=Coalesce(Sum("amount"), Value(0))
                )["total"],
            })
        context["hotel_stats"] = hotel_stats

        return context


class ToggleWishlistView(LoginRequiredMixin, View):
    """Toggle a hotel in/out of the user's wishlist."""

    def post(self, request, pk):
        hotel = get_object_or_404(Hotel, pk=pk)
        user = request.user

        if user.has_saved_hotel(hotel):
            user.saved_hotels.remove(hotel)
            messages.info(request, f"{hotel.name} removed from wishlist.")
        else:
            user.saved_hotels.add(hotel)
            messages.success(request, f"{hotel.name} saved to wishlist!")

        return redirect(request.META.get("HTTP_REFERER", "hotels:hotel_detail"))