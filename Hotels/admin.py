from django.contrib import admin
from .models import Hotel, Room
# Register your models here.
@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "owner", "is_active")
    list_filter = ("city", "is_active")
    search_fields = ("name", "city", "owner__username")

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ("name", "hotel", "price_per_night", "total_rooms", "is_active")
    list_filter = ("is_active", "hotel__city")
    search_fields = ("name", "hotel__name")
