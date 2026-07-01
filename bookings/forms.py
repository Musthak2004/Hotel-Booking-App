from datetime import date

from django import forms
from .models import Booking


class BookingForm(forms.ModelForm):

    promo_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Enter promo code (optional)"
        })
    )

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

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get("check_in")
        check_out = cleaned_data.get("check_out")
        guests = cleaned_data.get("guests")
        room = cleaned_data.get("room")

        # Validate date ordering: check_out must be after check_in
        if check_in and check_out:
            if check_out <= check_in:
                self.add_error("check_out", "Check-out date must be after check-in date.")

        # Validate check_in is not in the past
        if check_in and check_in < date.today():
            self.add_error("check_in", "Check-in date cannot be in the past.")

        # Validate capacity: guests must not exceed room capacity
        if guests and room and guests > room.capacity:
            self.add_error(
                "guests",
                f"This room can accommodate up to {room.capacity} guest(s).",
            )

        # Validate no overlapping bookings on the same room
        if check_in and check_out and room and check_out > check_in:
            overlapping = Booking.objects.filter(
                room=room,
                status__in=("pending", "confirmed"),
            ).filter(
                check_in__lt=check_out,
                check_out__gt=check_in,
            )
            # Exclude the current booking when updating an existing one
            if self.instance and self.instance.pk:
                overlapping = overlapping.exclude(pk=self.instance.pk)

            if overlapping.exists():
                raise forms.ValidationError(
                    "This room is already booked for the selected dates. "
                    "Please choose different dates or another room."
                )

        return cleaned_data