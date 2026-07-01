from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):

    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("owner", "Hotel Owner"),
    )

    email = models.EmailField(unique=True)

    phone_number = models.CharField(
        max_length=15,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="customer"
    )

    saved_hotels = models.ManyToManyField(
        "hotels.Hotel",
        blank=True,
        related_name="saved_by"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def has_saved_hotel(self, hotel):
        """Check if user has saved a specific hotel."""
        return self.saved_hotels.filter(pk=hotel.pk).exists()

    def __str__(self):
        return self.email


class Profile(models.Model):

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    address = models.TextField(blank=True)

    city = models.CharField(
        max_length=100,
        blank=True
    )

    country = models.CharField(
        max_length=100,
        blank=True
    )

    postal_code = models.CharField(
        max_length=20,
        blank=True
    )

    profile_picture = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.email