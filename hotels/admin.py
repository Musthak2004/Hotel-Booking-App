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
        "rating",
        "is_active",
        "created_at",
    )

    list_filter = (
        "is_active",
        "city",
        "country",
    )

    search_fields = (
        "name",
        "owner__username",
        "owner__email",
        "city",
        "country",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Hotel Information",
            {
                "fields": (
                    "owner",
                    "name",
                    "description",
                    "image",
                )
            },
        ),
        (
            "Location",
            {
                "fields": (
                    "address",
                    "city",
                    "country",
                    "latitude",
                    "longitude",
                )
            },
        ),
        (
            "Contact Information",
            {
                "fields": (
                    "phone_number",
                    "email",
                )
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "rating",
                    "is_active",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )