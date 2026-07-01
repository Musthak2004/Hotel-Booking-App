from django.urls import path
from .views import (
    HotelListView,
    HotelDetailView,
    HotelCreateView,
    HotelUpdateView,
    HotelDeleteView,
    OwnerDashboardView,
    ToggleWishlistView,
)

app_name = "hotels"

urlpatterns = [
    path("", HotelListView.as_view(), name="hotel_list"),
    path("<int:pk>/", HotelDetailView.as_view(), name="hotel_detail"),
    path("create/", HotelCreateView.as_view(), name="hotel_create"),
    path("<int:pk>/edit/", HotelUpdateView.as_view(), name="hotel_update"),
    path("<int:pk>/delete/", HotelDeleteView.as_view(), name="hotel_delete"),
    path(
        "owner/dashboard/",
        OwnerDashboardView.as_view(),
        name="owner_dashboard"
    ),
    path(
        "<int:pk>/wishlist/toggle/",
        ToggleWishlistView.as_view(),
        name="hotel_wishlist_toggle"
    ),
]