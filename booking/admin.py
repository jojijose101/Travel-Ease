from django.contrib import admin
from .models import Booking, VehicleBooking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "room", "check_in", "check_out", "status", "is_paid")
    list_filter = ("status", "is_paid")
    search_fields = ("user__username", "room__name", "room__hotel__name")


@admin.register(VehicleBooking)
class VehicleBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle', 'pickup_date', 'dropoff_date', 'units_count', 'status', 'is_paid')
    list_filter = ('status', 'is_paid', 'pickup_date')
    search_fields = ('user__username', 'vehicle__name', 'vehicle__shop__name')
