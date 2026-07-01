from django.contrib import admin
from .models import Room, PriceRule


class PriceRuleInline(admin.TabularInline):
    model = PriceRule
    extra = 1
    fields = ("name", "start_date", "end_date", "price_per_night")


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    inlines = [PriceRuleInline]

    list_display = (
        "id",
        "hotel",
        "room_number",
        "room_type",
        "price_per_night",
        "capacity",
        "total_rooms",
        "is_available",
    )

    list_select_related = ("hotel",)

    list_editable = (
        "price_per_night",
        "is_available",
    )

    search_fields = (
        "hotel__name",
        "room_number",
    )

    list_filter = (
        "room_type",
        "is_available",
        "capacity",
    )

    ordering = ("-created_at",)


@admin.register(PriceRule)
class PriceRuleAdmin(admin.ModelAdmin):

    list_display = ("id", "room", "name", "start_date", "end_date", "price_per_night")
    list_filter = ("start_date", "end_date")
    search_fields = ("name", "room__hotel__name")
    ordering = ("start_date",)
