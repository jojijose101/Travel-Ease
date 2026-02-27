from django.urls import path
from . import views

app_name = "Hotels"

urlpatterns = [

# Hotel Partner portal
path("partner/hotels/dashboard/", views.hotel_partner_dashboard, name="hotel_partner_dashboard"),
path("partner/hotels/hotels/", views.hotel_partner_hotels, name="hotel_partner_hotels"),
path("partner/hotels/hotel/add/", views.hotel_partner_hotel_add, name="hotel_partner_hotel_add"),
path("partner/hotels/hotel/<int:hotel_id>/edit/", views.hotel_partner_hotel_edit, name="hotel_partner_hotel_edit"),
path("partner/hotels/rooms/", views.hotel_partner_rooms, name="hotel_partner_rooms"),
path("partner/hotels/room/add/", views.hotel_partner_room_add, name="hotel_partner_room_add"),
path("partner/hotels/room/<int:room_id>/edit/", views.hotel_partner_room_edit, name="hotel_partner_room_edit"),
path("partner/hotels/bookings/", views.hotel_partner_bookings, name="hotel_partner_bookings"),
path("partner/hotels/bookings/<int:booking_id>/", views.partner_hotel_booking_detail, name="partner_hotel_booking_detail"),

]
