from django import forms
from .models import Room


class RoomForm(forms.ModelForm):

    class Meta:
        model = Room

        fields = [
            "hotel",
            "room_number",
            "room_type",
            "description",
            "price_per_night",
            "capacity",
            "total_rooms",
            "available_rooms",
            "image",
            "is_available",
        ]

        widgets = {
            "hotel": forms.Select(attrs={"class": "form-control"}),
            "room_number": forms.TextInput(attrs={"class": "form-control"}),
            "room_type": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "price_per_night": forms.NumberInput(attrs={"class": "form-control"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "total_rooms": forms.NumberInput(attrs={"class": "form-control"}),
            "available_rooms": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "is_available": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
