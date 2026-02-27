from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Coalesce


class RentalShop(models.Model):
    name = models.CharField(max_length=200)
    city = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    description = models.TextField(blank=True)
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

    logo = models.ImageField(upload_to='rental_shops/', blank=True, null=True)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rental_shops',
        null=True,
        blank=True,
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.city})"


class Vehicle(models.Model):
    VEHICLE_TYPE_CHOICES = (
        ('car', 'Car'),
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('van', 'Van'),
        ('suv', 'SUV'),
    )

    TRANSMISSION_CHOICES = (
        ('manual', 'Manual'),
        ('automatic', 'Automatic'),
    )

    shop = models.ForeignKey(RentalShop, on_delete=models.CASCADE, related_name='vehicles')
    name = models.CharField(max_length=200)  # e.g., "Swift Dzire" / "Activa 6G"
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPE_CHOICES, default='car')

    seats = models.PositiveIntegerField(default=4)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, default='manual')
    fuel = models.CharField(max_length=30, blank=True)  # Petrol/Diesel/Electric...

    price_per_day = models.DecimalField(max_digits=10, decimal_places=2)
    total_units = models.PositiveIntegerField(default=1)

    image = models.ImageField(upload_to='vehicles/', blank=True, null=True)

    is_active = models.BooleanField(default=True)

    def available_units(self, pickup_date, dropoff_date):
        booked = self.bookings.filter(
            status='confirmed',
            pickup_date__lt=dropoff_date,
            dropoff_date__gt=pickup_date,
        ).aggregate(total=Coalesce(Sum('units_count'), 0))['total']

        return max(self.total_units - booked, 0)

    def __str__(self):
        return f"{self.shop.name} - {self.name}"


