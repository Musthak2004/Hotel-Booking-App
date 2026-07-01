"""API URL routing."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import HotelViewSet, RoomViewSet

router = DefaultRouter()
router.register(r"hotels", HotelViewSet, basename="api-hotel")
router.register(r"rooms", RoomViewSet, basename="api-room")

urlpatterns = [
    path("", include(router.urls)),
]
