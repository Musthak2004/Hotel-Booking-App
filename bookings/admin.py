from django.contrib import admin
from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "room",
        "check_in",
        "check_out",
        "status",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__email",
        "room__room_number",
    )

    ordering = (
        "-created_at",
    )