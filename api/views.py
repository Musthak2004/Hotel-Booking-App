"""API viewsets for read-only hotel and room data."""

from rest_framework import viewsets, filters

from hotels.models import Hotel
from rooms.models import Room
from .serializers import HotelSerializer, HotelDetailSerializer, RoomSerializer


class HotelViewSet(viewsets.ReadOnlyModelViewSet):
    """List/retrieve hotels. Filterable by city, country, text search."""

    queryset = Hotel.objects.filter(is_active=True)
    filter_backends = [filters.SearchFilter]
    search_fields = ["name", "city", "country", "description"]

    def get_serializer_class(self):
        if self.action == "retrieve":
            return HotelDetailSerializer
        return HotelSerializer


class RoomViewSet(viewsets.ReadOnlyModelViewSet):
    """List/retrieve available rooms. Filterable by room_type, hotel."""

    queryset = Room.objects.filter(is_available=True)
    serializer_class = RoomSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["room_number", "hotel__name", "description"]

    def get_queryset(self):
        qs = super().get_queryset()
        room_type = self.request.query_params.get("room_type")
        hotel = self.request.query_params.get("hotel")
        min_price = self.request.query_params.get("min_price")
        max_price = self.request.query_params.get("max_price")
        if room_type:
            qs = qs.filter(room_type=room_type)
        if hotel:
            qs = qs.filter(hotel_id=hotel)
        if min_price:
            try:
                qs = qs.filter(price_per_night__gte=float(min_price))
            except ValueError:
                pass
        if max_price:
            try:
                qs = qs.filter(price_per_night__lte=float(max_price))
            except ValueError:
                pass
        return qs
