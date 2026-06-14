from django.urls import path

from .views import (
    BookingCreateView,
    BookingListView,
    BookingDetailView,
)

app_name = "bookings"

urlpatterns = [

    path(
        "",
        BookingListView.as_view(),
        name="booking_list"
    ),

    path(
        "create/",
        BookingCreateView.as_view(),
        name="booking_create"
    ),

    path(
        "<int:pk>/",
        BookingDetailView.as_view(),
        name="booking_detail"
    ),
]