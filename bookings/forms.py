from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):

    class Meta:
        model = Booking

        fields = (
            "room",
            "check_in",
            "check_out",
            "guests",
        )

        widgets = {
            "room": forms.Select(attrs={"class": "form-control"}),
            "check_in": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "check_out": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "guests": forms.NumberInput(attrs={"class": "form-control"}),
        }