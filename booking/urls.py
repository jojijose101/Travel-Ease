from django.urls import path
from . import views

app_name = "booking"

urlpatterns = [
    # Hotel booking views
    path("", views.hotel_list, name="hotel_list"),
    path("hotel/<int:hotel_id>/", views.hotel_detail, name="hotel_detail"),
    path("room/<int:room_id>/book/", views.book_room, name="book_room"),
    path("my-bookings/", views.my_bookings, name="my_bookings"),
    path("booking/<int:booking_id>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("payment/verify/", views.payment_verify, name="payment_verify"),
    path("my-bookings/<int:booking_id>/", views.customer_booking_detail, name="customer_booking_detail"),
    path("my-rentals/<int:booking_id>/", views.customer_rental_detail, name="customer_rental_detail"),


    # Authentication views
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),  
    path("signup/", views.signup_view, name="signup"),
    
]
