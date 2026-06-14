from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from hotels.models import Hotel
from .models import Room
from .forms import RoomForm
from .views import RoomListView, RoomDetailView, RoomCreateView, RoomUpdateView, RoomDeleteView

User = get_user_model()


class RoomModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )

    def test_create_room(self):
        room = Room.objects.create(
            hotel=self.hotel,
            room_number="101",
            room_type="double",
            price_per_night=150.00,
            capacity=2,
        )
        self.assertEqual(room.room_number, "101")
        self.assertEqual(room.room_type, "double")
        self.assertEqual(room.price_per_night, 150.00)
        self.assertEqual(room.capacity, 2)
        self.assertTrue(room.is_available)

    def test_string_representation(self):
        room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="single", price_per_night=100, capacity=1
        )
        self.assertEqual(str(room), "Test Hotel - 101")

    def test_default_values(self):
        room = Room.objects.create(
            hotel=self.hotel, room_number="102", room_type="single", price_per_night=100
        )
        self.assertEqual(room.capacity, 1)
        self.assertEqual(room.total_rooms, 1)
        self.assertEqual(room.available_rooms, 1)
        self.assertTrue(room.is_available)

    def test_ordering(self):
        Room.objects.create(hotel=self.hotel, room_number="A1", room_type="single", price_per_night=100)
        Room.objects.create(hotel=self.hotel, room_number="A2", room_type="double", price_per_night=200)
        rooms = Room.objects.all()
        self.assertEqual(rooms[0].room_number, "A2")


class RoomFormTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )

    def test_form_valid_data(self):
        form = RoomForm(data={
            "hotel": self.hotel.id,
            "room_number": "101",
            "room_type": "double",
            "price_per_night": "150.00",
            "capacity": 2,
            "total_rooms": 5,
            "available_rooms": 3,
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_required_room_number(self):
        form = RoomForm(data={
            "hotel": self.hotel.id,
            "room_number": "",
            "room_type": "single",
            "price_per_night": "100.00",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("room_number", form.errors)

    def test_form_missing_required_price(self):
        form = RoomForm(data={
            "hotel": self.hotel.id,
            "room_number": "101",
            "room_type": "single",
            "price_per_night": "",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("price_per_night", form.errors)

    def test_form_widgets_have_form_control(self):
        form = RoomForm()
        for field in ["hotel", "room_number", "room_type", "description", "price_per_night", "capacity", "total_rooms", "available_rooms", "image"]:
            self.assertIn("form-control", form.fields[field].widget.attrs.get("class", ""))


class RoomListViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        for i in range(3):
            Room.objects.create(
                hotel=self.hotel, room_number=f"10{i}", room_type="double",
                price_per_night=100 + i, capacity=2, is_available=True
            )
        Room.objects.create(
            hotel=self.hotel, room_number="999", room_type="single",
            price_per_night=50, capacity=1, is_available=False
        )

    def test_url_resolves_to_list_view(self):
        match = resolve("/rooms/")
        self.assertEqual(match.func.view_class, RoomListView)

    def test_url_name(self):
        response = self.client.get(reverse("rooms:room_list"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("rooms:room_list"))
        self.assertTemplateUsed(response, "rooms/room_list.html")

    def test_only_available_rooms_shown(self):
        response = self.client.get(reverse("rooms:room_list"))
        for room in response.context["rooms"]:
            self.assertTrue(room.is_available)
        self.assertEqual(len(response.context["rooms"]), 3)

    def test_filter_by_q_room_number(self):
        response = self.client.get(reverse("rooms:room_list"), {"q": "100"})
        self.assertEqual(len(response.context["rooms"]), 1)
        self.assertEqual(response.context["rooms"][0].room_number, "100")

    def test_filter_by_room_type(self):
        response = self.client.get(reverse("rooms:room_list"), {"room_type": "single"})
        self.assertEqual(len(response.context["rooms"]), 0)

    def test_context_has_current_filters(self):
        response = self.client.get(reverse("rooms:room_list"), {"q": "test", "room_type": "double"})
        self.assertEqual(response.context["current_q"], "test")
        self.assertEqual(response.context["current_room_type"], "double")


class RoomDetailViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="suite",
            price_per_night=300, capacity=4, description="Spacious suite"
        )

    def test_url_resolves_to_detail_view(self):
        match = resolve(f"/rooms/{self.room.id}/")
        self.assertEqual(match.func.view_class, RoomDetailView)

    def test_url_name(self):
        response = self.client.get(reverse("rooms:room_detail", args=[self.room.id]))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("rooms:room_detail", args=[self.room.id]))
        self.assertTemplateUsed(response, "rooms/room_detail.html")

    def test_context_contains_room(self):
        response = self.client.get(reverse("rooms:room_detail", args=[self.room.id]))
        self.assertEqual(response.context["room"], self.room)

    def test_404_for_non_existent_room(self):
        response = self.client.get(reverse("rooms:room_detail", args=[999]))
        self.assertEqual(response.status_code, 404)


class RoomCreateViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.customer = User.objects.create_user(
            username="cust1", email="cust@example.com", password="pass", role="customer"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )

    def test_url_resolves_to_create_view(self):
        match = resolve("/rooms/create/")
        self.assertEqual(match.func.view_class, RoomCreateView)

    def test_login_required(self):
        response = self.client.get(reverse("rooms:room_create"))
        self.assertRedirects(response, "/accounts/login/?next=/rooms/create/")

    def test_customer_cannot_create(self):
        self.client.force_login(self.customer)
        response = self.client.get(reverse("rooms:room_create"))
        self.assertRedirects(response, reverse("rooms:room_list"))

    def test_owner_can_create(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("rooms:room_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rooms/room_form.html")

    def test_owner_creates_room(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("rooms:room_create"), data={
            "hotel": self.hotel.id,
            "room_number": "201",
            "room_type": "deluxe",
            "price_per_night": "250.00",
            "capacity": 3,
            "total_rooms": 4,
            "available_rooms": 4,
        })
        self.assertRedirects(response, reverse("rooms:room_list"))
        self.assertTrue(Room.objects.filter(room_number="201").exists())


class RoomUpdateViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="own1", email="own@example.com", password="pass", role="owner"
        )
        self.other_owner = User.objects.create_user(
            username="other", email="other@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="301", room_type="single",
            price_per_night=100, capacity=1
        )

    def test_url_resolves_to_update_view(self):
        match = resolve(f"/rooms/{self.room.id}/edit/")
        self.assertEqual(match.func.view_class, RoomUpdateView)

    def test_login_required(self):
        response = self.client.get(reverse("rooms:room_update", args=[self.room.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/rooms/{self.room.id}/edit/")

    def test_wrong_owner_redirected(self):
        self.client.force_login(self.other_owner)
        response = self.client.get(reverse("rooms:room_update", args=[self.room.id]))
        self.assertRedirects(response, reverse("rooms:room_list"))

    def test_owner_can_update(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("rooms:room_update", args=[self.room.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "rooms/room_form.html")

    def test_owner_updates_room(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("rooms:room_update", args=[self.room.id]), data={
            "hotel": self.hotel.id,
            "room_number": "301",
            "room_type": "double",
            "price_per_night": "200.00",
            "capacity": 2,
            "total_rooms": 1,
            "available_rooms": 1,
            "is_available": True,
        })
        self.assertRedirects(response, reverse("rooms:room_list"))
        self.room.refresh_from_db()
        self.assertEqual(self.room.room_type, "double")
        self.assertEqual(self.room.price_per_night, 200.00)


class RoomDeleteViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="own1", email="own@example.com", password="pass", role="owner"
        )
        self.other = User.objects.create_user(
            username="other", email="other@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="401", room_type="single",
            price_per_night=100, capacity=1
        )

    def test_url_resolves_to_delete_view(self):
        match = resolve(f"/rooms/{self.room.id}/delete/")
        self.assertEqual(match.func.view_class, RoomDeleteView)

    def test_login_required(self):
        response = self.client.get(reverse("rooms:room_delete", args=[self.room.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/rooms/{self.room.id}/delete/")

    def test_wrong_owner_redirected(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("rooms:room_delete", args=[self.room.id]))
        self.assertRedirects(response, reverse("rooms:room_list"))

    def test_owner_can_delete_room(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("rooms:room_delete", args=[self.room.id]))
        self.assertRedirects(response, reverse("rooms:room_list"))
        self.assertFalse(Room.objects.filter(id=self.room.id).exists())
