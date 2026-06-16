from django.db import models
from accounts.models import CustomUser


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
