from django.urls import path

from .views import (
    BookingCreateView,
    BookingListView,
    BookingDetailView,
    BookingCancelView,
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

    path(
        "<int:pk>/cancel/",
        BookingCancelView.as_view(),
        name="booking_cancel"
    ),
]
