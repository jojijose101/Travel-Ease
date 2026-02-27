from django.conf import settings
from django.db import models
from django.core.validators import RegexValidator

phone_validator = RegexValidator(
    regex=r'^\+?\d{10,15}$',
    message="Enter a valid mobile number (10–15 digits). Example: +919876543210"
)

class Profile(models.Model):
    ROLE_CUSTOMER = 'customer'
    ROLE_HOTEL_PARTNER = 'hotel_partner'
    ROLE_RENTAL_PARTNER = 'rental_partner'

    ROLE_CHOICES = (
        (ROLE_CUSTOMER, 'Customer'),
        (ROLE_HOTEL_PARTNER, 'Hotel Partner'),
        (ROLE_RENTAL_PARTNER, 'Rental Partner'),
    )

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_CUSTOMER)
    mobile_number = models.CharField(
        max_length=15,
        validators=[phone_validator],
        unique=True,
        null=True,
        blank=True
    )
    def __str__(self):
        return f"{self.user.username} ({self.role})"
