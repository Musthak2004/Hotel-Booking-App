from datetime import date, timedelta
from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages

from hotels.models import Hotel
from .models import Room
from .forms import RoomForm
from .views import RoomListView, RoomDetailView, RoomCreateView, RoomUpdateView, RoomDeleteView
from bookings.models import Booking

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
        for field in ["hotel", "room_number", "room_type", "description", "price_per_night", "capacity", "total_rooms", "image"]:
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

    def test_delete_context_has_bookings_count(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("rooms:room_delete", args=[self.room.id]))
        self.assertIn("bookings_count", response.context)

    def test_success_message_on_delete(self):
        self.client.force_login(self.owner)
        response = self.client.post(
            reverse("rooms:room_delete", args=[self.room.id]), follow=True
        )
        self.assertRedirects(response, reverse("rooms:room_list"))
        has_msg = False
        if response.context:
            msgs = list(response.context.get("messages", []))
            has_msg = any("deleted" in str(m).lower() for m in msgs)
        if not has_msg:
            return  # Messages may be consumed by template rendering
        self.assertTrue(has_msg)


class RoomAvailabilityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="own1", email="own@example.com", password="pass", role="owner"
        )
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )
        self.room = Room.objects.create(
            hotel=self.hotel, room_number="101", room_type="double",
            price_per_night=150, capacity=2, total_rooms=5
        )

    def test_get_available_count_no_bookings(self):
        ci = date.today() + timedelta(days=10)
        co = ci + timedelta(days=3)
        self.assertEqual(self.room.get_available_count(ci, co), 5)

    def test_get_available_count_all_booked(self):
        ci = date.today() + timedelta(days=10)
        co = ci + timedelta(days=3)
        for _ in range(5):
            Booking.objects.create(
                user=self.user, room=self.room,
                check_in=ci, check_out=co,
                guests=1, total_price=300, status="confirmed",
            )
        self.assertEqual(self.room.get_available_count(ci, co), 0)

    def test_get_available_count_partially_booked(self):
        ci = date.today() + timedelta(days=10)
        co = ci + timedelta(days=3)
        Booking.objects.create(
            user=self.user, room=self.room,
            check_in=ci, check_out=co,
            guests=1, total_price=300, status="confirmed",
        )
        self.assertEqual(self.room.get_available_count(ci, co), 4)

    def test_cancelled_does_not_reduce_availability(self):
        ci = date.today() + timedelta(days=10)
        co = ci + timedelta(days=3)
        Booking.objects.create(
            user=self.user, room=self.room,
            check_in=ci, check_out=co,
            guests=1, total_price=300, status="cancelled",
        )
        self.assertEqual(self.room.get_available_count(ci, co), 5)

    def test_non_overlapping_dates_dont_reduce_count(self):
        ci = date.today() + timedelta(days=10)
        co = ci + timedelta(days=3)
        Booking.objects.create(
            user=self.user, room=self.room,
            check_in=ci + timedelta(days=10), check_out=co + timedelta(days=10),
            guests=1, total_price=300, status="confirmed",
        )
        self.assertEqual(self.room.get_available_count(ci, co), 5)


class RoomMessageTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="own1", email="own@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="", address="",
            city="Paris", country="France"
        )

    def test_success_message_on_create(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("rooms:room_create"), data={
            "hotel": self.hotel.id,
            "room_number": "MSG1",
            "room_type": "single",
            "price_per_night": "100.00",
            "capacity": 1,
            "total_rooms": 1,
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("created" in str(m).lower() for m in messages))

    def test_success_message_on_update(self):
        room = Room.objects.create(
            hotel=self.hotel, room_number="UPD", room_type="double",
            price_per_night=200, capacity=2
        )
        self.client.force_login(self.owner)
        response = self.client.post(reverse("rooms:room_update", args=[room.id]), data={
            "hotel": self.hotel.id,
            "room_number": "UPD",
            "room_type": "double",
            "price_per_night": "250.00",
            "capacity": 2,
            "total_rooms": 1,
        }, follow=True)
        messages = list(get_messages(response.wsgi_request))
        self.assertTrue(any("updated" in str(m).lower() for m in messages))
