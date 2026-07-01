from django.db import models
from accounts.models import CustomUser


class Amenity(models.Model):
    """Amenities that hotels can offer (WiFi, pool, breakfast, etc.)."""

    name = models.CharField(max_length=100, unique=True)
    icon = models.CharField(
        max_length=50, blank=True,
        help_text="Emoji or CSS class for display"
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Amenities"

    def __str__(self):
        return self.name


class HotelImage(models.Model):
    """Additional images for a hotel gallery."""

    hotel = models.ForeignKey(
        "Hotel", on_delete=models.CASCADE, related_name="gallery_images"
    )
    image = models.ImageField(upload_to="hotels/gallery/")
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"Image for {self.hotel.name}"


class Hotel(models.Model):

    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="hotels"
    )

    name = models.CharField(max_length=200)
    description = models.TextField()

    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)

    image = models.ImageField(
        upload_to="hotels/",
        blank=True,
        null=True
    )

    amenities = models.ManyToManyField(
        Amenity, blank=True, related_name="hotels"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_image_url(self):
        try:
            return self.image.url if self.image else None
        except Exception:
            return None

    def average_rating(self):
        """Return the average rating for this hotel, or None if no reviews."""
        from django.db.models import Avg
        result = self.reviews.aggregate(avg=Avg("rating"))
        return result["avg"]

    def review_count(self):
        """Return the total number of reviews for this hotel."""
        return self.reviews.count()
