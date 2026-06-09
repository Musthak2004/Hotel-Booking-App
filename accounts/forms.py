from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Profile


class CustomUserRegistrationForm(UserCreationForm):

    class Meta:
        model = CustomUser

        fields = (
            "username",
            "email",
            "phone_number",
            "role",
            "password1",
            "password2",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "role": forms.Select(
                attrs={"class": "form-select"}
            ),
        }

    password1 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        )
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control"}
        )
    )


class CustomUserUpdateForm(forms.ModelForm):

    class Meta:
        model = CustomUser

        fields = (
            "username",
            "email",
            "phone_number",
        )

        widgets = {
            "username": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "email": forms.EmailInput(
                attrs={"class": "form-control"}
            ),
            "phone_number": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = Profile

        fields = (
            "address",
            "city",
            "country",
            "postal_code",
            "profile_picture",
        )

        widgets = {
            "address": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 3
                }
            ),
            "city": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "country": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "postal_code": forms.TextInput(
                attrs={"class": "form-control"}
            ),
        }