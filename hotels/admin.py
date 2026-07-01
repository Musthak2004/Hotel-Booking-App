from django.contrib import admin
from .models import Hotel, Amenity, HotelImage
from rooms.models import Room


class RoomInline(admin.TabularInline):
    model = Room
    extra = 1
    fields = ("room_number", "room_type", "price_per_night", "capacity", "is_available")


class HotelImageInline(admin.TabularInline):
    model = HotelImage
    extra = 1
    fields = ("image", "is_primary", "order")


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    inlines = [RoomInline, HotelImageInline]

    list_display = (
        "id",
        "name",
        "owner",
        "city",
        "country",
        "is_active",
        "created_at",
    )

    list_select_related = ("owner",)

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
        "amenities",
    )

    filter_horizontal = ("amenities",)

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    readonly_fields = ("created_at", "updated_at")


@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):

    list_display = ("id", "name", "icon")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(HotelImage)
class HotelImageAdmin(admin.ModelAdmin):

    list_display = ("id", "hotel", "is_primary", "order")
    list_filter = ("is_primary",)
    search_fields = ("hotel__name",)
