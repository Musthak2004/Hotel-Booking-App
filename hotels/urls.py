from django.urls import path
from .views import HotelListView

app_name = "hotels"

urlpatterns = [
    path("", HotelListView.as_view(), name="hotel_list"),
]