from datetime import date
import hashlib
import hmac

import razorpay
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.utils import role_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.dateparse import parse_date
from django.views.decorators.csrf import csrf_exempt

from .models import RentalShop, Vehicle
from .forms import RentalShopForm, VehicleForm
from booking.models import VehicleBooking
from django.core.exceptions import PermissionDenied



# -------------------------
# Customer vehicle rental views
# -------------------------


def vehicle_list(request):
    q = (request.GET.get('q') or '').strip()
    city = (request.GET.get('city') or '').strip()
    vtype = (request.GET.get('type') or '').strip()

    vehicles = Vehicle.objects.select_related('shop').filter(is_active=True, shop__is_active=True).order_by('name')

    if q:
        vehicles = vehicles.filter(name__icontains=q)
    if city:
        vehicles = vehicles.filter(shop__city__icontains=city)
    if vtype:
        vehicles = vehicles.filter(vehicle_type=vtype)

    return render(request, 'vehicles/vehicle_list.html', {
        'vehicles': vehicles,
        'q': q,
        'city': city,
        'type': vtype,
    })


def shop_detail(request, shop_id):
    shop = get_object_or_404(RentalShop, id=shop_id, is_active=True)
    vehicles = shop.vehicles.filter(is_active=True).order_by('price_per_day')

    pickup_raw = (request.GET.get('pickup') or '').strip()
    dropoff_raw = (request.GET.get('dropoff') or '').strip()

    pickup = parse_date(pickup_raw) if pickup_raw else None
    dropoff = parse_date(dropoff_raw) if dropoff_raw else None

    availability = {}
    if pickup and dropoff and pickup < dropoff:
        for v in vehicles:
            availability[v.id] = v.available_units(pickup, dropoff)

    return render(request, 'vehicles/shop_detail.html', {
        'shop': shop,
        'vehicles': vehicles,
        'pickup': pickup_raw,
        'dropoff': dropoff_raw,
        'availability': availability,
    })


def vehicle_detail(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle.objects.select_related('shop'), id=vehicle_id, is_active=True, shop__is_active=True)

    pickup_raw = (request.GET.get('pickup') or '').strip()
    dropoff_raw = (request.GET.get('dropoff') or '').strip()

    pickup = parse_date(pickup_raw) if pickup_raw else None
    dropoff = parse_date(dropoff_raw) if dropoff_raw else None

    available = None
    if pickup and dropoff and pickup < dropoff:
        available = vehicle.available_units(pickup, dropoff)

    return render(request, 'vehicles/vehicle_detail.html', {
        'vehicle': vehicle,
        'shop': vehicle.shop,
        'pickup': pickup_raw,
        'dropoff': dropoff_raw,
        'available': available,
    })


@login_required
def book_vehicle(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle.objects.select_related('shop'), id=vehicle_id, is_active=True, shop__is_active=True)

    errors = {}
    preview_available = None

    pickup_q = (request.GET.get('pickup') or '').strip()
    dropoff_q = (request.GET.get('dropoff') or '').strip()

    if request.method == 'POST':
        values = {
            'pickup_date': (request.POST.get('pickup_date') or '').strip(),
            'dropoff_date': (request.POST.get('dropoff_date') or '').strip(),
            'units_count': (request.POST.get('units_count') or '1').strip(),
            'pickup_location': (request.POST.get('pickup_location') or '').strip(),
            'dropoff_location': (request.POST.get('dropoff_location') or '').strip(),
            'mobile_number': (request.POST.get('mobile_number') or '').strip(),
        }
    else:
        values = {
            'pickup_date': pickup_q,
            'dropoff_date': dropoff_q,
            'units_count': '1',
            'pickup_location': vehicle.shop.city,
            'dropoff_location': vehicle.shop.city,
            'mobile_number': getattr(getattr(request.user, 'profile', None), 'mobile_number', ''),
        }

    if request.method == 'POST':
        pickup_raw = values['pickup_date']
        dropoff_raw = values['dropoff_date']
        units_raw = values['units_count']
        mobile_raw = values.get('mobile_number', '')

        pickup_date = None
        dropoff_date = None

        if not pickup_raw:
            errors['pickup_date'] = 'Pickup date is required.'
        else:
            try:
                pickup_date = date.fromisoformat(pickup_raw)
            except ValueError:
                errors['pickup_date'] = 'Invalid pickup date format.'

        if not dropoff_raw:
            errors['dropoff_date'] = 'Drop-off date is required.'
        else:
            try:
                dropoff_date = date.fromisoformat(dropoff_raw)
            except ValueError:
                errors['dropoff_date'] = 'Invalid drop-off date format.'

        try:
            units_count = int(units_raw)
            if units_count < 1:
                errors['units_count'] = 'Units must be at least 1.'
        except ValueError:
            errors['units_count'] = 'Units must be a number.'
            units_count = None

        # Mobile number validation (optional)
        if mobile_raw:
            digits = mobile_raw.replace('+', '')
            if not digits.isdigit() or not (10 <= len(digits) <= 15):
                errors['mobile_number'] = 'Enter a valid mobile number (10–15 digits).'

        today = date.today()
        if pickup_date and dropoff_date:
            if pickup_date >= dropoff_date:
                errors['dropoff_date'] = 'Drop-off must be after pickup.'
            if pickup_date < today:
                errors['pickup_date'] = 'Pickup cannot be in the past.'

        if not errors and pickup_date and dropoff_date and units_count is not None:
            preview_available = vehicle.available_units(pickup_date, dropoff_date)
            if units_count > preview_available:
                errors['units_count'] = f'Only {preview_available} unit(s) available for these dates.'
            else:
                days = (dropoff_date - pickup_date).days
                amount = int(days * units_count * float(vehicle.price_per_day) * 100)  # paise

                booking = VehicleBooking.objects.create(
                    user=request.user,
                    vehicle=vehicle,
                    mobile_number=mobile_raw or None,
                    pickup_date=pickup_date,
                    dropoff_date=dropoff_date,
                    pickup_location=values.get('pickup_location', ''),
                    dropoff_location=values.get('dropoff_location', ''),
                    units_count=units_count,
                    status='confirmed',
                    is_paid=False,
                    amount_paise=amount,
                )

                # Store to profile if empty
                try:
                    if mobile_raw and hasattr(request.user, 'profile') and not request.user.profile.mobile_number:
                        request.user.profile.mobile_number = mobile_raw
                        request.user.profile.save(update_fields=['mobile_number'])
                except Exception:
                    pass

                client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
                raz_order = client.order.create({
                    'amount': amount,
                    'currency': 'INR',
                    'payment_capture': 1,
                    'receipt': f'vehicle_booking_{booking.id}',
                })

                booking.razorpay_order_id = raz_order['id']
                booking.save()

                return render(request, 'vehicles/pay_now.html', {
                    'booking': booking,
                    'vehicle': vehicle,
                    'shop': vehicle.shop,
                    'razorpay_key_id': settings.RAZORPAY_KEY_ID,
                    'razorpay_order_id': booking.razorpay_order_id,
                    'amount': amount,
                    'callback_url': request.build_absolute_uri(reverse('vehicles:payment_verify_vehicle')),
                })

    return render(request, 'vehicles/book_vehicle.html', {
        'vehicle': vehicle,
        'shop': vehicle.shop,
        'errors': errors,
        'values': values,
        'preview_available': preview_available,
    })


@login_required
@csrf_exempt
def payment_verify_vehicle(request):
    if request.method != 'POST':
        return redirect('vehicles:vehicle_list')

    razorpay_order_id = request.POST.get('razorpay_order_id')
    razorpay_payment_id = request.POST.get('razorpay_payment_id')
    razorpay_signature = request.POST.get('razorpay_signature')

    booking = get_object_or_404(VehicleBooking, razorpay_order_id=razorpay_order_id)

    payload = f"{razorpay_order_id}|{razorpay_payment_id}".encode()
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    if expected == razorpay_signature:
        booking.razorpay_payment_id = razorpay_payment_id
        booking.razorpay_signature = razorpay_signature
        booking.is_paid = True
        booking.save()
        messages.success(request, '✅ Payment successful! Vehicle rental confirmed.')
        return redirect('vehicles:my_rentals')

    booking.status = 'cancelled'
    booking.save()
    messages.error(request, '❌ Payment verification failed.')
    return redirect('vehicles:my_rentals')


@login_required
def my_rentals(request):
    rentals = (
        VehicleBooking.objects
        .filter(user=request.user)
        .select_related('vehicle', 'vehicle__shop')
        .order_by('-created_at')
    )
    return render(request, 'vehicles/my_rentals.html', {'rentals': rentals})


@login_required
def cancel_rental(request, booking_id):
    booking = get_object_or_404(
        VehicleBooking.objects.select_related('vehicle', 'vehicle__shop'),
        id=booking_id,
        user=request.user,
    )

    if request.method == 'POST':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Rental cancelled.')
        return redirect('vehicles:my_rentals')

    return render(request, 'vehicles/cancel_rental.html', {'booking': booking})


@role_required(['rental_partner'])
def rental_partner_dashboard(request):
    shops = RentalShop.objects.filter(owner=request.user).order_by('-id')
    vehicles = Vehicle.objects.filter(shop__owner=request.user).select_related('shop').order_by('-id')[:10]
    bookings = VehicleBooking.objects.filter(vehicle__shop__owner=request.user).select_related('vehicle', 'vehicle__shop', 'user').order_by('-created_at')[:10]
    return render(request, "partners/rentals/dashboard.html", {
        "shops": shops,
        "vehicles": vehicles,
        "bookings": bookings,
    })

@role_required(['rental_partner'])
def rental_partner_shops(request):
    shops = RentalShop.objects.filter(owner=request.user).order_by('-id')
    return render(request, "partners/rentals/shops_list.html", {"shops": shops})

@role_required(['rental_partner'])
def rental_partner_shop_add(request):
    if request.method == "POST":
        form = RentalShopForm(request.POST, request.FILES)
        if form.is_valid():
            shop = form.save(commit=False)
            shop.owner = request.user
            shop.save()
            messages.success(request, "Rental shop added.")
            return redirect("vehicles:rental_partner_shops")
    else:
        form = RentalShopForm()
    return render(request, "partners/rentals/shop_form.html", {"form": form, "mode": "add"})

@role_required(['rental_partner'])
def rental_partner_shop_edit(request, shop_id):
    shop = get_object_or_404(RentalShop, id=shop_id, owner=request.user)
    if request.method == "POST":
        form = RentalShopForm(request.POST, request.FILES, instance=shop)
        if form.is_valid():
            form.save()
            messages.success(request, "Rental shop updated.")
            return redirect("vehicles:rental_partner_shops")
    else:
        form = RentalShopForm(instance=shop)
    return render(request, "partners/rentals/shop_form.html", {"form": form, "mode": "edit"})

@role_required(['rental_partner'])
def rental_partner_vehicles(request):
    vehicles = Vehicle.objects.filter(shop__owner=request.user).select_related('shop').order_by('-id')
    return render(request, "partners/rentals/vehicles_list.html", {"vehicles": vehicles})

@role_required(['rental_partner'])
def rental_partner_vehicle_add(request):
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES, owner=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle added.")
            return redirect("vehicles:rental_partner_vehicles")
    else:
        form = VehicleForm(owner=request.user)
    return render(request, "partners/rentals/vehicle_form.html", {"form": form, "mode": "add"})

@role_required(['rental_partner'])
def rental_partner_vehicle_edit(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, shop__owner=request.user)
    if request.method == "POST":
        form = VehicleForm(request.POST, request.FILES, instance=vehicle, owner=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Vehicle updated.")
            return redirect("vehicles:rental_partner_vehicles")
    else:
        form = VehicleForm(instance=vehicle, owner=request.user)
    return render(request, "partners/rentals/vehicle_form.html", {"form": form, "mode": "edit"})

@role_required(['rental_partner'])
def rental_partner_bookings(request):
    bookings = VehicleBooking.objects.filter(vehicle__shop__owner=request.user).select_related('vehicle', 'vehicle__shop', 'user').order_by('-created_at')
    return render(request, "partners/rentals/bookings_list.html", {"bookings": bookings})


@role_required(['rental_partner'])
def partner_rental_booking_detail(request, booking_id):
    """
    Rental partner sees bookings for ONLY their shop vehicles.
    Must filter by ownership (shop.owner == request.user).
    """
    if getattr(request.user, "profile", None) and request.user.profile.role != "rental_partner":
        raise PermissionDenied("Not allowed")

    booking = get_object_or_404(VehicleBooking, id=booking_id)

    # IMPORTANT: adjust relationship names:
    # Example assumes: VehicleBooking -> Vehicle -> RentalShop and RentalShop has owner field
    shop = booking.vehicle.shop
    if shop.owner_id != request.user.id:
        raise PermissionDenied("Not allowed")

    return render(
        request,
        "partners/rentals/partner_rental_booking_detail.html",
        {"booking": booking, "shop": shop},
    )