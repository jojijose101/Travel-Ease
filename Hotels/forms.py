from django import forms
from .models import Hotel, Room

class HotelForm(forms.ModelForm):
    class Meta:
        model = Hotel
        fields = ['name', 'city', 'address', 'description', 'image', 'mobile_number','is_active']

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['hotel', 'name', 'capacity', 'price_per_night', 'total_rooms', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        if owner is not None:
            self.fields['hotel'].queryset = Hotel.objects.filter(owner=owner)
