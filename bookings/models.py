from datetime import date

from django.db import models
from accounts.models import CustomUser
from rooms.models import Room


class Booking(models.Model):

    STATUS_CHOICES = (
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    room = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    check_in = models.DateField()

    check_out = models.DateField()

    guests = models.PositiveIntegerField(default=1)

    total_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.user.email} - {self.room}"


class PromoCode(models.Model):
    """Promotional discount codes that can be applied to bookings."""

    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.PositiveIntegerField(
        help_text="Percentage discount (1-100)"
    )
    max_uses = models.PositiveIntegerField(
        default=0,
        help_text="0 = unlimited"
    )
    used_count = models.PositiveIntegerField(default=0)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_valid(self):
        """Check if this promo code is currently valid."""
        today = date.today()
        return (
            self.is_active
            and self.valid_from.date() <= today
            and self.valid_until.date() >= today
            and (self.max_uses == 0 or self.used_count < self.max_uses)
        )

    def apply_discount(self, amount):
        """Apply the percentage discount to the given amount."""
        return amount * (100 - self.discount_percent) / 100

    def __str__(self):
        return self.code