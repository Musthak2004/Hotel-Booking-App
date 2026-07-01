from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, ListView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from .forms import CustomUserRegistrationForm, CustomUserUpdateForm, ProfileUpdateForm
from .models import Profile, CustomUser

class SignUpView(CreateView):
    form_class = CustomUserRegistrationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"

class ContactPageView(TemplateView):
    template_name = "registration/contact.html"

@login_required
def profile_update(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == "POST":
        user_form = CustomUserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect("home")
    else:
        user_form = CustomUserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        "user_form": user_form,
        "profile_form": profile_form,
    }
    return render(request, "registration/profile_update.html", context)


class SavedHotelsListView(LoginRequiredMixin, ListView):
    """Display the user's saved hotels."""
    template_name = "accounts/wishlist.html"
    context_object_name = "hotels"

    def get_queryset(self):
        return self.request.user.saved_hotels.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["wishlist_count"] = self.get_queryset().count()
        return context
