from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import Coalesce
from Hotels.models import Hotel, Room
from vehicles.models import Vehicle


class Booking(models.Model):
    STATUS_CHOICES = (
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    mobile_number = models.CharField(max_length=15, blank=True, null=True)
    check_in = models.DateField()
    check_out = models.DateField()
    rooms_count = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="confirmed")
    created_at = models.DateTimeField(auto_now_add=True)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    amount_paise = models.PositiveIntegerField(default=0)  # total in paise


    def clean(self):
        if self.check_in >= self.check_out:
            raise ValidationError("Check-out must be after check-in.")
        if self.check_in < timezone.now().date():
            raise ValidationError("Check-in cannot be in the past.")


class VehicleBooking(models.Model):
    STATUS_CHOICES = (
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='bookings')
    mobile_number = models.CharField(max_length=15, blank=True, null=True)

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
