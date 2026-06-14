from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import CustomUserRegistrationForm, CustomUserUpdateForm, ProfileUpdateForm

# Create your views here.

class SignUpView(CreateView):
    form_class = CustomUserRegistrationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

@login_required
def profile_update(request):
    if request.method == "POST":
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("home")
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "registration/profile_update.html", context)
