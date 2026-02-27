from django.contrib import admin
from .models import RentalShop, Vehicle


@admin.register(RentalShop)
class RentalShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'is_active', 'owner')
    search_fields = ('name', 'city')
    list_filter = ('city', 'is_active')


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ('name', 'vehicle_type', 'shop', 'city', 'price_per_day', 'total_units', 'is_active')
    search_fields = ('name', 'shop__name', 'shop__city')
    list_filter = ('vehicle_type', 'transmission', 'is_active', 'shop__city')

    def city(self, obj):
        return obj.shop.city


