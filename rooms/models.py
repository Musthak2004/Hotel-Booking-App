from django.db import models
from hotels.models import Hotel


class RoomImage(models.Model):
    """Additional images for a room gallery."""

    room = models.ForeignKey(
        "Room", on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ImageField(upload_to="rooms/gallery/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for Room #{self.room_id}"


class Room(models.Model):

    ROOM_TYPES = (
        ("single", "Single"),
        ("double", "Double"),
        ("deluxe", "Deluxe"),
        ("suite", "Suite"),
        ("family", "Family"),
    )

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="rooms"
    )

    room_number = models.CharField(max_length=20)

    room_type = models.CharField(
        max_length=20,
        choices=ROOM_TYPES
    )

    description = models.TextField(blank=True)

    price_per_night = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    capacity = models.PositiveIntegerField(default=1)

    total_rooms = models.PositiveIntegerField(default=1)

    image = models.ImageField(
        upload_to="rooms/",
        blank=True,
        null=True
    )

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.hotel.name} - {self.room_number}"

    def get_available_count(self, check_in, check_out):
        """Return how many rooms of this type are available for the given date range."""
        from bookings.models import Booking
        booked = Booking.objects.filter(
            room=self,
            status__in=("pending", "confirmed"),
            check_in__lt=check_out,
            check_out__gt=check_in,
        ).count()
        return max(0, self.total_rooms - booked)


class PriceRule(models.Model):
    """Seasonal pricing rule for a room."""
    room = models.ForeignKey(
        Room, on_delete=models.CASCADE, related_name="price_rules"
    )
    name = models.CharField(max_length=100, help_text="e.g. Summer 2026")
    start_date = models.DateField()
    end_date = models.DateField()
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["start_date"]

    def __str__(self):
        return f"{self.name} — {self.room}"