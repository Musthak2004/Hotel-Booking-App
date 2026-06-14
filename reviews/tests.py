from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from hotels.models import Hotel
from .models import Review
from .forms import ReviewForm
from .views import ReviewCreateView, ReviewUpdateView, ReviewDeleteView

User = get_user_model()


class ReviewModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
        )
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="Nice place",
            address="123 St", city="Paris", country="France"
        )

    def test_create_review(self):
        review = Review.objects.create(
            user=self.user, hotel=self.hotel, rating=5, comment="Great!"
        )
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Great!")
        self.assertEqual(review.user, self.user)
        self.assertEqual(review.hotel, self.hotel)

    def test_string_representation(self):
        review = Review.objects.create(
            user=self.user, hotel=self.hotel, rating=4, comment="Good"
        )
        self.assertIn(self.user.email, str(review))
        self.assertIn(self.hotel.name, str(review))

    def test_unique_constraint(self):
        Review.objects.create(
            user=self.user, hotel=self.hotel, rating=5, comment="First"
        )
        with self.assertRaises(Exception):
            Review.objects.create(
                user=self.user, hotel=self.hotel, rating=3, comment="Duplicate"
            )

    def test_ordering_newest_first(self):
        hotel2 = Hotel.objects.create(
            owner=self.owner, name="Hotel 2", description="",
            address="456 St", city="London", country="UK"
        )
        r1 = Review.objects.create(
            user=self.user, hotel=self.hotel, rating=4, comment="Older"
        )
        r2 = Review.objects.create(
            user=self.user, hotel=hotel2, rating=5, comment="Newer"
        )
        self.assertGreater(r2.created_at, r1.created_at)

    def test_rating_choices(self):
        hotels = []
        for i in range(5):
            h = Hotel.objects.create(
                owner=self.owner, name=f"Hotel {i}", description="",
                address=f"{i} St", city="Paris", country="France"
            )
            hotels.append(h)
            review = Review.objects.create(
                user=self.user, hotel=h, rating=i + 1, comment="OK"
            )
            self.assertEqual(review.rating, i + 1)


class ReviewFormTests(TestCase):
    def test_form_valid_data(self):
        form = ReviewForm(data={
            "rating": 5,
            "comment": "Amazing stay!",
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_rating(self):
        form = ReviewForm(data={"comment": "Nice"})
        self.assertFalse(form.is_valid())
        self.assertIn("rating", form.errors)

    def test_form_missing_comment(self):
        form = ReviewForm(data={"rating": 4})
        self.assertFalse(form.is_valid())
        self.assertIn("comment", form.errors)

    def test_form_widgets_have_form_control(self):
        form = ReviewForm()
        for field in ["rating", "comment"]:
            self.assertIn("form-control", form.fields[field].widget.attrs.get("class", ""))


class ReviewCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
        )
        self.other_user = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass"
        )
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="Nice",
            address="123 St", city="Paris", country="France"
        )

    def test_url_resolves_to_create_view(self):
        match = resolve(f"/reviews/create/{self.hotel.id}/")
        self.assertEqual(match.func.view_class, ReviewCreateView)

    def test_login_required(self):
        response = self.client.get(
            reverse("reviews:review_create", args=[self.hotel.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/reviews/create/{self.hotel.id}/"
        )

    def test_uses_correct_template(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("reviews:review_create", args=[self.hotel.id])
        )
        self.assertTemplateUsed(response, "reviews/review_form.html")

    def test_context_contains_hotel(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("reviews:review_create", args=[self.hotel.id])
        )
        self.assertEqual(response.context["hotel"], self.hotel)

    def test_creates_review_and_redirects(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("reviews:review_create", args=[self.hotel.id]),
            data={"rating": 5, "comment": "Excellent!"},
        )
        self.assertRedirects(
            response,
            reverse("hotels:hotel_detail", args=[self.hotel.id])
        )
        review = Review.objects.get(user=self.user, hotel=self.hotel)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, "Excellent!")

    def test_redirects_if_review_already_exists(self):
        existing = Review.objects.create(
            user=self.user, hotel=self.hotel, rating=3, comment="Meh"
        )
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("reviews:review_create", args=[self.hotel.id]),
            data={"rating": 5, "comment": "Amazing!"},
        )
        self.assertRedirects(
            response,
            reverse("reviews:review_update", args=[existing.id])
        )
        review = Review.objects.get(user=self.user, hotel=self.hotel)
        self.assertEqual(review.comment, "Meh")
        self.assertEqual(review.rating, 3)

    def test_404_for_non_existent_hotel(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("reviews:review_create", args=[999]))
        self.assertEqual(response.status_code, 404)


class ReviewUpdateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
        )
        self.other_user = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass"
        )
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="Nice",
            address="123 St", city="Paris", country="France"
        )
        self.review = Review.objects.create(
            user=self.user, hotel=self.hotel, rating=4, comment="Good"
        )

    def test_url_resolves_to_update_view(self):
        match = resolve(f"/reviews/{self.review.id}/edit/")
        self.assertEqual(match.func.view_class, ReviewUpdateView)

    def test_login_required(self):
        response = self.client.get(
            reverse("reviews:review_update", args=[self.review.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/reviews/{self.review.id}/edit/"
        )

    def test_other_user_cannot_edit(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("reviews:review_update", args=[self.review.id])
        )
        self.assertRedirects(response, reverse("hotels:hotel_list"))

    def test_owner_can_edit(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("reviews:review_update", args=[self.review.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/review_form.html")

    def test_updates_review(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("reviews:review_update", args=[self.review.id]),
            data={"rating": 5, "comment": "Updated!"},
        )
        self.assertRedirects(
            response,
            reverse("hotels:hotel_detail", args=[self.hotel.id])
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, "Updated!")

    def test_context_contains_hotel(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("reviews:review_update", args=[self.review.id])
        )
        self.assertEqual(response.context["hotel"], self.hotel)


class ReviewDeleteViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="user1", email="user@example.com", password="pass"
        )
        self.other_user = User.objects.create_user(
            username="user2", email="user2@example.com", password="pass"
        )
        self.owner = User.objects.create_user(
            username="owner1", email="owner@example.com", password="pass", role="owner"
        )
        self.hotel = Hotel.objects.create(
            owner=self.owner, name="Test Hotel", description="Nice",
            address="123 St", city="Paris", country="France"
        )
        self.review = Review.objects.create(
            user=self.user, hotel=self.hotel, rating=4, comment="Good"
        )

    def test_url_resolves_to_delete_view(self):
        match = resolve(f"/reviews/{self.review.id}/delete/")
        self.assertEqual(match.func.view_class, ReviewDeleteView)

    def test_login_required(self):
        response = self.client.get(
            reverse("reviews:review_delete", args=[self.review.id])
        )
        self.assertRedirects(
            response,
            f"/accounts/login/?next=/reviews/{self.review.id}/delete/"
        )

    def test_other_user_cannot_delete(self):
        self.client.force_login(self.other_user)
        response = self.client.get(
            reverse("reviews:review_delete", args=[self.review.id])
        )
        self.assertRedirects(response, reverse("hotels:hotel_list"))

    def test_owner_can_delete(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("reviews:review_delete", args=[self.review.id])
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reviews/review_confirm_delete.html")

    def test_deletes_review(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse("reviews:review_delete", args=[self.review.id])
        )
        self.assertRedirects(
            response,
            reverse("hotels:hotel_detail", args=[self.hotel.id])
        )
        self.assertFalse(Review.objects.filter(id=self.review.id).exists())
