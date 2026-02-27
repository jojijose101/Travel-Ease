from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [

    # Customer vehicle rental
    path('', views.vehicle_list, name='vehicle_list'),
    path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('<int:vehicle_id>/book/', views.book_vehicle, name='book_vehicle'),
    path('payment/verify/', views.payment_verify_vehicle, name='payment_verify_vehicle'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('my-rentals/<int:booking_id>/cancel/', views.cancel_rental, name='cancel_rental'),
    
    path("partner/rentals/dashboard/", views.rental_partner_dashboard, name="rental_partner_dashboard"),
    path("partner/rentals/shops/", views.rental_partner_shops, name="rental_partner_shops"),
    path("partner/rentals/shop/add/", views.rental_partner_shop_add, name="rental_partner_shop_add"),
    path("partner/rentals/shop/<int:shop_id>/edit/", views.rental_partner_shop_edit, name="rental_partner_shop_edit"),
    path("partner/rentals/vehicles/", views.rental_partner_vehicles, name="rental_partner_vehicles"),
    path("partner/rentals/vehicle/add/", views.rental_partner_vehicle_add, name="rental_partner_vehicle_add"),
    path("partner/rentals/vehicle/<int:vehicle_id>/edit/", views.rental_partner_vehicle_edit, name="rental_partner_vehicle_edit"),
    path("partner/rentals/bookings/", views.rental_partner_bookings, name="rental_partner_bookings"),
    path("partner/rentals/bookings/<int:booking_id>/", views.partner_rental_booking_detail, name="partner_rental_booking_detail"),

]

