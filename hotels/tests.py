from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from .models import Hotel
from .forms import HotelForm
from .views import HotelListView, HotelDetailView, HotelCreateView, HotelUpdateView, HotelDeleteView

User = get_user_model()


class HotelModelTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )

    def test_create_hotel(self):
        hotel = Hotel.objects.create(
            owner=self.owner,
            name="Test Hotel",
            description="A nice place to stay",
            address="123 Main St",
            city="New York",
            country="USA",
        )
        self.assertEqual(hotel.name, "Test Hotel")
        self.assertEqual(hotel.city, "New York")
        self.assertEqual(hotel.owner, self.owner)
        self.assertTrue(hotel.is_active)

    def test_string_representation(self):
        hotel = Hotel.objects.create(
            owner=self.owner, name="Grand Hotel", description="", address="", city="Paris", country="France"
        )
        self.assertEqual(str(hotel), "Grand Hotel")

    def test_default_active(self):
        hotel = Hotel.objects.create(
            owner=self.owner, name="Hotel", description="", address="", city="Paris", country="France"
        )
        self.assertTrue(hotel.is_active)

    def test_optional_fields_blank(self):
        hotel = Hotel.objects.create(
            owner=self.owner, name="Hotel", description="", address="", city="Paris", country="France"
        )
        self.assertEqual(hotel.phone_number, "")
        self.assertEqual(hotel.email, "")
        self.assertFalse(hotel.image)


class HotelFormTests(TestCase):
    def test_form_valid_data(self):
        form = HotelForm(data={
            "name": "Test Hotel",
            "description": "Nice hotel",
            "address": "123 Main St",
            "city": "New York",
            "country": "USA",
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_required_name(self):
        form = HotelForm(data={
            "name": "",
            "description": "Nice hotel",
            "address": "123 Main St",
            "city": "New York",
            "country": "USA",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("name", form.errors)

    def test_form_missing_required_city(self):
        form = HotelForm(data={
            "name": "Test Hotel",
            "description": "Nice hotel",
            "address": "123 Main St",
            "city": "",
            "country": "USA",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("city", form.errors)

    def test_form_widgets_have_form_control(self):
        form = HotelForm()
        for field_name in ["name", "description", "address", "city", "country", "phone_number", "email"]:
            self.assertIn("form-control", form.fields[field_name].widget.attrs.get("class", ""))


class HotelListViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        for i in range(3):
            Hotel.objects.create(
                owner=self.owner,
                name=f"Hotel {i}",
                description="",
                address="",
                city="New York" if i % 2 == 0 else "Paris",
                country="USA" if i % 2 == 0 else "France",
            )
        Hotel.objects.create(
            owner=self.owner, name="Inactive Hotel", description="", address="",
            city="London", country="UK", is_active=False
        )

    def test_url_resolves_to_list_view(self):
        match = resolve("/hotels/")
        self.assertEqual(match.func.view_class, HotelListView)

    def test_url_name(self):
        response = self.client.get(reverse("hotels:hotel_list"))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("hotels:hotel_list"))
        self.assertTemplateUsed(response, "hotels/hotel_list.html")

    def test_only_active_hotels_in_context(self):
        response = self.client.get(reverse("hotels:hotel_list"))
        self.assertEqual(len(response.context["hotels"]), 3)
        for hotel in response.context["hotels"]:
            self.assertTrue(hotel.is_active)

    def test_filter_by_q(self):
        response = self.client.get(reverse("hotels:hotel_list"), {"q": "Hotel 0"})
        self.assertEqual(len(response.context["hotels"]), 1)
        self.assertEqual(response.context["hotels"][0].name, "Hotel 0")

    def test_filter_by_city(self):
        response = self.client.get(reverse("hotels:hotel_list"), {"city": "Paris"})
        self.assertEqual(len(response.context["hotels"]), 1)

    def test_sort_by_name(self):
        response = self.client.get(reverse("hotels:hotel_list"), {"sort": "name"})
        names = [h.name for h in response.context["hotels"]]
        self.assertEqual(names, sorted(names))

    def test_context_has_cities(self):
        response = self.client.get(reverse("hotels:hotel_list"))
        self.assertIn("cities", response.context)
        self.assertIn("New York", response.context["cities"])
        self.assertIn("Paris", response.context["cities"])

    def test_context_has_current_filters(self):
        response = self.client.get(reverse("hotels:hotel_list"), {"q": "test", "city": "Paris"})
        self.assertEqual(response.context["current_q"], "test")
        self.assertEqual(response.context["current_city"], "Paris")

    def test_pagination_context(self):
        for i in range(10):
            Hotel.objects.create(
                owner=self.owner, name=f"Extra Hotel {i}", description="", address="",
                city="London", country="UK"
            )
        response = self.client.get(reverse("hotels:hotel_list"))
        self.assertTrue(response.context["is_paginated"])
        self.assertEqual(len(response.context["hotels"]), 9)


class HotelDetailViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Detail Hotel", description="Great place",
            address="456 Oak Ave", city="Boston", country="USA"
        )

    def test_url_resolves_to_detail_view(self):
        match = resolve(f"/hotels/{self.hotel.id}/")
        self.assertEqual(match.func.view_class, HotelDetailView)

    def test_url_name(self):
        response = self.client.get(reverse("hotels:hotel_detail", args=[self.hotel.id]))
        self.assertEqual(response.status_code, 200)

    def test_uses_correct_template(self):
        response = self.client.get(reverse("hotels:hotel_detail", args=[self.hotel.id]))
        self.assertTemplateUsed(response, "hotels/hotel_detail.html")

    def test_context_contains_hotel(self):
        response = self.client.get(reverse("hotels:hotel_detail", args=[self.hotel.id]))
        self.assertEqual(response.context["hotel"], self.hotel)

    def test_404_for_non_existent_hotel(self):
        response = self.client.get(reverse("hotels:hotel_detail", args=[999]))
        self.assertEqual(response.status_code, 404)


class HotelCreateViewTests(TestCase):
    def test_url_resolves_to_create_view(self):
        match = resolve("/hotels/create/")
        self.assertEqual(match.func.view_class, HotelCreateView)

    def test_login_required(self):
        response = self.client.get(reverse("hotels:hotel_create"))
        self.assertRedirects(response, "/accounts/login/?next=/hotels/create/")

    def test_customer_cannot_create(self):
        customer = User.objects.create_user(
            username="cust1", email="cust@example.com", password="pass", role="customer"
        )
        self.client.force_login(customer)
        response = self.client.get(reverse("hotels:hotel_create"))
        self.assertRedirects(response, reverse("hotels:hotel_list"))

    def test_owner_can_create(self):
        owner = User.objects.create_user(
            username="own1", email="own@example.com", password="pass", role="owner"
        )
        self.client.force_login(owner)
        response = self.client.get(reverse("hotels:hotel_create"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotels/hotel_form.html")

    def test_owner_create_sets_owner_and_redirects(self):
        owner = User.objects.create_user(
            username="own2", email="own2@example.com", password="pass", role="owner"
        )
        self.client.force_login(owner)
        response = self.client.post(reverse("hotels:hotel_create"), data={
            "name": "New Hotel",
            "description": "Desc",
            "address": "123 St",
            "city": "Paris",
            "country": "France",
        })
        self.assertRedirects(response, reverse("hotels:hotel_list"))
        hotel = Hotel.objects.get(name="New Hotel")
        self.assertEqual(hotel.owner, owner)


class HotelUpdateViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="own1", email="own@example.com", password="pass", role="owner"
        )
        self.other = User.objects.create_user(
            username="other", email="other@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Update Hotel", description="", address="",
            city="Paris", country="France"
        )

    def test_url_resolves_to_update_view(self):
        match = resolve(f"/hotels/{self.hotel.id}/edit/")
        self.assertEqual(match.func.view_class, HotelUpdateView)

    def test_login_required(self):
        response = self.client.get(reverse("hotels:hotel_update", args=[self.hotel.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/hotels/{self.hotel.id}/edit/")

    def test_wrong_owner_redirected(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("hotels:hotel_update", args=[self.hotel.id]))
        self.assertRedirects(response, reverse("hotels:hotel_list"))

    def test_owner_can_update(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("hotels:hotel_update", args=[self.hotel.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotels/hotel_form.html")

    def test_owner_updates_hotel(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("hotels:hotel_update", args=[self.hotel.id]), data={
            "name": "Updated Name",
            "description": "Updated desc",
            "address": "456 New St",
            "city": "London",
            "country": "UK",
        })
        self.assertRedirects(response, reverse("hotels:hotel_list"))
        self.hotel.refresh_from_db()
        self.assertEqual(self.hotel.name, "Updated Name")
        self.assertEqual(self.hotel.city, "London")


class HotelDeleteViewTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            username="own1", email="own@example.com", password="pass", role="owner"
        )
        self.other = User.objects.create_user(
            username="other", email="other@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Delete Hotel", description="", address="",
            city="Paris", country="France"
        )

    def test_url_resolves_to_delete_view(self):
        match = resolve(f"/hotels/{self.hotel.id}/delete/")
        self.assertEqual(match.func.view_class, HotelDeleteView)

    def test_login_required(self):
        response = self.client.get(reverse("hotels:hotel_delete", args=[self.hotel.id]))
        self.assertRedirects(response, f"/accounts/login/?next=/hotels/{self.hotel.id}/delete/")

    def test_wrong_owner_redirected(self):
        self.client.force_login(self.other)
        response = self.client.get(reverse("hotels:hotel_delete", args=[self.hotel.id]))
        self.assertRedirects(response, reverse("hotels:hotel_list"))

    def test_owner_can_delete(self):
        self.client.force_login(self.owner)
        response = self.client.get(reverse("hotels:hotel_delete", args=[self.hotel.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "hotels/hotel_confirm_delete.html")

    def test_owner_deletes_hotel(self):
        self.client.force_login(self.owner)
        response = self.client.post(reverse("hotels:hotel_delete", args=[self.hotel.id]))
        self.assertRedirects(response, reverse("hotels:hotel_list"))
        self.assertFalse(Hotel.objects.filter(id=self.hotel.id).exists())
