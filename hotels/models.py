from django.db import models


class Hotel(models.Model):

    owner = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="hotels"
    )

    name = models.CharField(max_length=200)

    description = models.TextField()

    address = models.TextField()

    city = models.CharField(max_length=100)

    country = models.CharField(max_length=100)

    phone_number = models.CharField(max_length=15)

    email = models.EmailField()

    rating = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0.0
    )

    image = models.ImageField(
        upload_to="hotels/",
        blank=True,
        null=True
    )

    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name