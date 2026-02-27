from django.db import models
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import Coalesce


# Create your models here.
class Hotel(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    image = models.ImageField(
        upload_to="hotels/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="hotels",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.name} ({self.city})"


class Room(models.Model):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name="rooms")
    name = models.CharField(max_length=120)
    capacity = models.PositiveIntegerField(default=2)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    total_rooms = models.PositiveIntegerField(default=1)

    image = models.ImageField(
        upload_to="rooms/",
        blank=True,
        null=True
    )

    is_active = models.BooleanField(default=True)

    def available_rooms(self, check_in, check_out):
        # bookings that overlap with selected range
        booked = self.bookings.filter(
            status="confirmed",
            check_in__lt=check_out,
            check_out__gt=check_in
        ).aggregate(total=Coalesce(Sum("rooms_count"), 0))["total"]

        return max(self.total_rooms - booked, 0)


    def __str__(self):
        return f"{self.hotel.name} - {self.name}"