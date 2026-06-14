from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "hotel",
        "room_number",
        "room_type",
        "price_per_night",
        "available_rooms",
        "is_available",
    )

    search_fields = (
        "hotel__name",
        "room_number",
    )

    list_filter = (
        "room_type",
        "is_available",
    )

    ordering = ("-created_at",)