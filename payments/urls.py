from django.urls import path

from . import webhooks
from .views import (
    PaymentCheckoutView,
    PaymentDetailView,
    PaymentSuccessView,
    PaymentCancelledView,
)

app_name = "payments"

urlpatterns = [
    path(
        "checkout/<int:booking_id>/",
        PaymentCheckoutView.as_view(),
        name="payment_checkout",
    ),
    path(
        "success/<int:booking_id>/",
        PaymentSuccessView.as_view(),
        name="payment_success",
    ),
    path(
        "cancelled/<int:booking_id>/",
        PaymentCancelledView.as_view(),
        name="payment_cancelled",
    ),
    path(
        "<int:pk>/",
        PaymentDetailView.as_view(),
        name="payment_detail",
    ),
    path(
        "webhook/",
        webhooks.stripe_webhook,
        name="stripe_webhook",
    ),
]
