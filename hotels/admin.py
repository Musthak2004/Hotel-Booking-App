from django.contrib import admin
from .models import Hotel


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "owner",
        "city",
        "country",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "city",
        "country",
        "owner__email",
    )

    list_filter = (
        "city",
        "country",
        "is_active",
    )

    ordering = ("-created_at",)

    readonly_fields = ("created_at", "updated_at")