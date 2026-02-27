from django import forms
from .models import RentalShop, Vehicle

class RentalShopForm(forms.ModelForm):
    class Meta:
        model = RentalShop
        fields = ['name', 'city', 'address', 'description', 'mobile_number', 'logo', 'is_active']

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['shop', 'name', 'vehicle_type', 'seats', 'transmission', 'fuel', 'price_per_day', 'total_units', 'image', 'is_active']

    def __init__(self, *args, **kwargs):
        owner = kwargs.pop('owner', None)
        super().__init__(*args, **kwargs)
        if owner is not None:
            self.fields['shop'].queryset = RentalShop.objects.filter(owner=owner)
