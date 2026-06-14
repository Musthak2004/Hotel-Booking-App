from django.urls import path

from .views import (
    ReviewCreateView,
    ReviewUpdateView,
    ReviewDeleteView,
)

app_name = "reviews"

urlpatterns = [

    path(
        "create/<int:hotel_id>/",
        ReviewCreateView.as_view(),
        name="review_create"
    ),

    path(
        "<int:pk>/edit/",
        ReviewUpdateView.as_view(),
        name="review_update"
    ),

    path(
        "<int:pk>/delete/",
        ReviewDeleteView.as_view(),
        name="review_delete"
    ),
]