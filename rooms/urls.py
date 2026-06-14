from django.urls import path

from .views import (
    RoomListView,
    RoomDetailView,
    RoomCreateView,
    RoomUpdateView,
    RoomDeleteView,
)

app_name = "rooms"

urlpatterns = [

    path(
        "",
        RoomListView.as_view(),
        name="room_list"
    ),

    path(
        "<int:pk>/",
        RoomDetailView.as_view(),
        name="room_detail"
    ),

    path(
        "create/",
        RoomCreateView.as_view(),
        name="room_create"
    ),

    path(
        "<int:pk>/edit/",
        RoomUpdateView.as_view(),
        name="room_update"
    ),

    path(
        "<int:pk>/delete/",
        RoomDeleteView.as_view(),
        name="room_delete"
    ),
]