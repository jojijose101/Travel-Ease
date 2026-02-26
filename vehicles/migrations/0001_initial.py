# Generated manually for the vehicles app.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='RentalShop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=120)),
                ('address', models.TextField(blank=True)),
                ('description', models.TextField(blank=True)),
                ('logo', models.ImageField(blank=True, null=True, upload_to='rental_shops/')),
                ('is_active', models.BooleanField(default=True)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='rental_shops', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Vehicle',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('vehicle_type', models.CharField(choices=[('car', 'Car'), ('bike', 'Bike'), ('scooter', 'Scooter'), ('van', 'Van'), ('suv', 'SUV')], default='car', max_length=20)),
                ('seats', models.PositiveIntegerField(default=4)),
                ('transmission', models.CharField(choices=[('manual', 'Manual'), ('automatic', 'Automatic')], default='manual', max_length=20)),
                ('fuel', models.CharField(blank=True, max_length=30)),
                ('price_per_day', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total_units', models.PositiveIntegerField(default=1)),
                ('image', models.ImageField(blank=True, null=True, upload_to='vehicles/')),
                ('is_active', models.BooleanField(default=True)),
                ('shop', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='vehicles', to='vehicles.rentalshop')),
            ],
        ),
        migrations.CreateModel(
            name='VehicleBooking',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pickup_date', models.DateField()),
                ('dropoff_date', models.DateField()),
                ('pickup_location', models.CharField(blank=True, max_length=200)),
                ('dropoff_location', models.CharField(blank=True, max_length=200)),
                ('units_count', models.PositiveIntegerField(default=1)),
                ('status', models.CharField(choices=[('confirmed', 'Confirmed'), ('cancelled', 'Cancelled')], default='confirmed', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('razorpay_order_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_payment_id', models.CharField(blank=True, max_length=100, null=True)),
                ('razorpay_signature', models.CharField(blank=True, max_length=255, null=True)),
                ('is_paid', models.BooleanField(default=False)),
                ('amount_paise', models.PositiveIntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('vehicle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bookings', to='vehicles.vehicle')),
            ],
        ),
    ]
