from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from accounts.utils import get_role, role_required
from .models import Hotel, Room
from booking.models import Booking
from .forms import HotelForm, RoomForm
from django.core.exceptions import PermissionDenied


@role_required(['hotel_partner'])
def hotel_partner_dashboard(request):
    hotels = Hotel.objects.filter(owner=request.user).order_by('-id')
    rooms = Room.objects.filter(hotel__owner=request.user).select_related('hotel').order_by('-id')[:10]
    bookings = Booking.objects.filter(room__hotel__owner=request.user).select_related('room', 'room__hotel', 'user').order_by('-created_at')[:10]
    return render(request, "partners/hotels/dashboard.html", {
        "hotels": hotels,
        "rooms": rooms,
        "bookings": bookings,
    })

@role_required(['hotel_partner'])
def hotel_partner_hotels(request):
    hotels = Hotel.objects.filter(owner=request.user).order_by('-id')
    return render(request, "partners/hotels/hotels_list.html", {"hotels": hotels})

@role_required(['hotel_partner'])
def hotel_partner_hotel_add(request):
    if request.method == "POST":
        form = HotelForm(request.POST, request.FILES)
        if form.is_valid():
            hotel = form.save(commit=False)
            hotel.owner = request.user
            hotel.save()
            messages.success(request, "Hotel added.")
            return redirect("Hotels:hotel_partner_hotels")
    else:
        form = HotelForm()
    return render(request, "partners/hotels/hotel_form.html", {"form": form, "mode": "add"})

@role_required(['hotel_partner'])
def hotel_partner_hotel_edit(request, hotel_id):
    hotel = get_object_or_404(Hotel, id=hotel_id, owner=request.user)
    if request.method == "POST":
        form = HotelForm(request.POST, request.FILES, instance=hotel)
        if form.is_valid():
            form.save()
            messages.success(request, "Hotel updated.")
            return redirect("Hotels:hotel_partner_hotels")
    else:
        form = HotelForm(instance=hotel)
    return render(request, "partners/hotels/hotel_form.html", {"form": form, "mode": "edit"})

@role_required(['hotel_partner'])
def hotel_partner_rooms(request):
    rooms = Room.objects.filter(hotel__owner=request.user).select_related('hotel').order_by('-id')
    return render(request, "partners/hotels/rooms_list.html", {"rooms": rooms})

@role_required(['hotel_partner'])
def hotel_partner_room_add(request):
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES, owner=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Room added.")
            return redirect("Hotels:hotel_partner_rooms")
    else:
        form = RoomForm(owner=request.user)
    return render(request, "partners/hotels/room_form.html", {"form": form, "mode": "add"})

@role_required(['hotel_partner'])
def hotel_partner_room_edit(request, room_id):
    room = get_object_or_404(Room, id=room_id, hotel__owner=request.user)
    if request.method == "POST":
        form = RoomForm(request.POST, request.FILES, instance=room, owner=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Room updated.")
            return redirect("Hotels:hotel_partner_rooms")
    else:
        form = RoomForm(instance=room, owner=request.user)
    return render(request, "partners/hotels/room_form.html", {"form": form, "mode": "edit"})

@role_required(['hotel_partner'])
def hotel_partner_bookings(request):
    bookings = Booking.objects.filter(room__hotel__owner=request.user).select_related('room', 'room__hotel', 'user').order_by('-created_at')
    return render(request, "partners/hotels/bookings_list.html", {"bookings": bookings})

@role_required(['hotel_partner'])
def partner_hotel_booking_detail(request, booking_id):
    """
    Hotel partner sees bookings for ONLY their hotels.
    Must filter by ownership (hotel.owner == request.user).
    """
    if getattr(request.user, "profile", None) and request.user.profile.role != "hotel_partner":
        raise PermissionDenied("Not allowed")

    booking = get_object_or_404(Booking, id=booking_id)

    # IMPORTANT: adjust relationship names to match your project:
    # Example assumes: Booking -> Room -> Hotel and Hotel has owner field
    hotel = booking.room.hotel
    if hotel.owner_id != request.user.id:
        raise PermissionDenied("Not allowed")

    return render(
        request,
        "partners/Hotels/partner_hotel_booking_detail.html",
        {"booking": booking, "hotel": hotel},
    )