from django.urls import path
from . import views

app_name = 'vehicles'

urlpatterns = [
    path('', views.vehicle_list, name='vehicle_list'),
    path('shop/<int:shop_id>/', views.shop_detail, name='shop_detail'),
    path('<int:vehicle_id>/', views.vehicle_detail, name='vehicle_detail'),
    path('<int:vehicle_id>/book/', views.book_vehicle, name='book_vehicle'),
    path('payment/verify/', views.payment_verify_vehicle, name='payment_verify_vehicle'),
    path('my-rentals/', views.my_rentals, name='my_rentals'),
    path('my-rentals/<int:booking_id>/cancel/', views.cancel_rental, name='cancel_rental'),
]
