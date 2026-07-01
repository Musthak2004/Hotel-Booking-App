from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "booking",
        "amount",
        "payment_method",
        "status",
        "stripe_session_id",
        "paid_at",
        "created_at",
    )

    list_select_related = ("booking",)

    list_editable = ("status",)

    list_filter = (
        "status",
        "payment_method",
        "paid_at",
    )

    search_fields = (
        "transaction_id",
        "stripe_session_id",
        "booking__id",
    )

    ordering = ("-created_at",)

    date_hierarchy = "created_at"

    readonly_fields = ("stripe_session_id", "transaction_id", "paid_at")
