from django.db import models
from hotels.models import Hotel


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

    available_rooms = models.PositiveIntegerField(default=1)

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