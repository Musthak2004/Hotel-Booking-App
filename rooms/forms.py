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
            "image",
        ]

        widgets = {
            "hotel": forms.Select(attrs={"class": "form-control"}),
            "room_number": forms.TextInput(attrs={"class": "form-control"}),
            "room_type": forms.Select(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "price_per_night": forms.NumberInput(attrs={"class": "form-control"}),
            "capacity": forms.NumberInput(attrs={"class": "form-control"}),
            "total_rooms": forms.NumberInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user is not None and user.is_authenticated:
            self.fields["hotel"].queryset = user.hotels.all()
