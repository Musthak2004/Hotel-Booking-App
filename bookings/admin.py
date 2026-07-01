from django.contrib import admin
from django.contrib import messages

from .models import Booking, PromoCode
from payments.models import Payment


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0
    fields = ("amount", "payment_method", "status", "stripe_session_id", "paid_at")
    readonly_fields = ("stripe_session_id", "paid_at")
    can_delete = False


@admin.action(description="Mark selected bookings as confirmed")
def mark_confirmed(modeladmin, request, queryset):
    updated = queryset.exclude(status="confirmed").update(status="confirmed")
    messages.success(request, f"{updated} booking(s) marked as confirmed.")


@admin.action(description="Mark selected bookings as cancelled")
def mark_cancelled(modeladmin, request, queryset):
    updated = queryset.exclude(status="cancelled").update(status="cancelled")
    messages.success(request, f"{updated} booking(s) marked as cancelled.")


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    inlines = [PaymentInline]

    list_display = (
        "id",
        "user",
        "room",
        "check_in",
        "check_out",
        "guests",
        "total_price",
        "status",
        "created_at",
    )

    list_select_related = ("user", "room__hotel")

    list_editable = ("status",)

    list_filter = (
        "status",
        "check_in",
        "check_out",
    )

    search_fields = (
        "user__email",
        "room__room_number",
        "room__hotel__name",
    )

    ordering = ("-created_at",)

    date_hierarchy = "check_in"

    actions = [mark_confirmed, mark_cancelled]


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "code",
        "discount_percent",
        "max_uses",
        "used_count",
        "valid_from",
        "valid_until",
        "is_active",
    )

    list_editable = ("is_active",)

    list_filter = ("is_active", "valid_from", "valid_until")

    search_fields = ("code",)

    ordering = ("-created_at",)
