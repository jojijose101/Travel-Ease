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


class VehicleBooking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')

    pickup_date = models.DateField()
    dropoff_date = models.DateField()

    pickup_location = models.CharField(max_length=200, blank=True)
    dropoff_location = models.CharField(max_length=200, blank=True)

    units_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    created_at = models.DateTimeField(auto_now_add=True)

    # Razorpay fields (same pattern as hotel booking)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    amount_paise = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.pickup_date >= self.dropoff_date:
            raise ValidationError('Drop-off must be after pickup.')
        if self.pickup_date < timezone.now().date():
            raise ValidationError('Pickup cannot be in the past.')

    def __str__(self):
        return f"{self.user} - {self.vehicle.name} ({self.pickup_date} to {self.dropoff_date})"
