from django import forms
from .models import Hotel, Amenity


class HotelForm(forms.ModelForm):

    class Meta:
        model = Hotel

        fields = [
            "name",
            "description",
            "address",
            "city",
            "country",
            "phone_number",
            "email",
            "image",
            "amenities",
        ]

        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control"}),
            "address": forms.Textarea(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "country": forms.TextInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "amenities": forms.CheckboxSelectMultiple(attrs={"class": ""}),
        }