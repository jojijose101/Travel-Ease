# hotel_booking
## Vehicle Rental Module

This project now includes a **Vehicle Rental** section (Option A architecture) as a separate Django app.

- Browse vehicles: `/vehicles/`
- Vehicle detail: `/vehicles/<vehicle_id>/`
- Book a vehicle: `/vehicles/<vehicle_id>/book/`
- My rentals: `/vehicles/my-rentals/`

### Setup
1. Add the app (already added in this zip): `vehicles`
2. Run migrations:
   - `python manage.py makemigrations vehicles`
   - `python manage.py migrate`
3. Add data via Django Admin (`/admin/`):
   - Rental Shops
   - Vehicles

The Vehicle UI uses a **white + light red** theme and the navbar provides a clear **Hotels | Vehicles** switch.
