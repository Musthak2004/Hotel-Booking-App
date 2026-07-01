"""API serializers for read-only hotel and room data."""

from rest_framework import serializers
from hotels.models import Hotel
from rooms.models import Room


class RoomSerializer(serializers.ModelSerializer):
    """Room list/detail serializer."""

    hotel_name = serializers.CharField(source="hotel.name", read_only=True)
    room_type_display = serializers.CharField(
        source="get_room_type_display", read_only=True
    )

    class Meta:
        model = Room
        fields = [
            "id",
            "hotel",
            "hotel_name",
            "room_number",
            "room_type",
            "room_type_display",
            "description",
            "price_per_night",
            "capacity",
            "total_rooms",
            "image",
            "is_available",
        ]


class HotelSerializer(serializers.ModelSerializer):
    """Hotel list serializer (lightweight, no nested rooms)."""

    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    amenities = serializers.StringRelatedField(many=True)

    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "description",
            "city",
            "country",
            "image",
            "is_active",
            "amenities",
            "average_rating",
            "review_count",
            "created_at",
        ]

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_review_count(self, obj):
        return obj.review_count()


class HotelDetailSerializer(serializers.ModelSerializer):
    """Hotel detail serializer (includes rooms)."""

    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    amenities = serializers.StringRelatedField(many=True)
    rooms = RoomSerializer(many=True, read_only=True)

    class Meta:
        model = Hotel
        fields = [
            "id",
            "name",
            "description",
            "address",
            "city",
            "country",
            "phone_number",
            "email",
            "image",
            "is_active",
            "amenities",
            "rooms",
            "average_rating",
            "review_count",
            "created_at",
        ]

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_review_count(self, obj):
        return obj.review_count()
