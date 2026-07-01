from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import (
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from hotels.models import Hotel

from .models import Review
from .forms import ReviewForm


class ReviewCreateView(
    LoginRequiredMixin,
    CreateView
):

    model = Review

    form_class = ReviewForm

    template_name = (
        "reviews/review_form.html"
    )

    def dispatch(self, *args, **kwargs):
        self.hotel = get_object_or_404(
            Hotel, pk=self.kwargs["hotel_id"]
        )
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.hotel
        return context

    def form_valid(self, form):
        existing = Review.objects.filter(
            user=self.request.user, hotel=self.hotel
        ).first()
        if existing:
            messages.error(
                self.request,
                "You have already reviewed this hotel."
            )
            return redirect(
                "reviews:review_update", pk=existing.pk
            )
        form.instance.user = self.request.user
        form.instance.hotel = self.hotel
        messages.success(self.request, "Review added successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "hotels:hotel_detail",
            kwargs={"pk": self.hotel.id}
        )


class ReviewUpdateView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    UpdateView
):

    model = Review

    form_class = ReviewForm

    template_name = (
        "reviews/review_form.html"
    )

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request,
            "You can only edit your own reviews."
        )
        return redirect("hotels:hotel_list")

    def form_valid(self, form):
        messages.success(self.request, "Review updated successfully!")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["hotel"] = self.object.hotel
        return context

    def get_success_url(self):
        return reverse(
            "hotels:hotel_detail",
            kwargs={"pk": self.object.hotel.id}
        )


class ReviewDeleteView(
    LoginRequiredMixin,
    UserPassesTestMixin,
    DeleteView
):

    model = Review

    template_name = (
        "reviews/review_confirm_delete.html"
    )

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Review deleted successfully!")
        return super().delete(request, *args, **kwargs)

    def test_func(self):
        review = self.get_object()
        return self.request.user == review.user

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        messages.error(
            self.request,
            "You can only delete your own reviews."
        )
        return redirect("hotels:hotel_list")

    def get_success_url(self):
        return reverse(
            "hotels:hotel_detail",
            kwargs={"pk": self.object.hotel.id}
        )
