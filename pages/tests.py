from django.test import TestCase
from django.urls import reverse, resolve

from .views import HomePageView


class HomePageURLTests(TestCase):
    def test_home_url_resolves_to_homepageview(self):
        match = resolve("/")
        self.assertEqual(match.func.view_class, HomePageView)

    def test_home_url_name(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)

    def test_home_url_name_reverse(self):
        self.assertEqual(reverse("home"), "/")


class HomePageViewTests(TestCase):
    def test_uses_correct_template(self):
        response = self.client.get(reverse("home"))
        self.assertTemplateUsed(response, "home.html")

    def test_contains_expected_content(self):
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Find your perfect")
        self.assertContains(response, "Popular hotels")
        self.assertContains(response, "Why choose us")
        self.assertContains(response, "Ready to book your stay?")

    def test_status_code_200(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_shows_welcome_message_for_authenticated_user(self):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass"
        )
        self.client.force_login(user)
        response = self.client.get(reverse("home"))
        self.assertContains(response, "Welcome back, testuser!")

    def test_no_welcome_message_for_anonymous_user(self):
        response = self.client.get(reverse("home"))
        self.assertNotContains(response, "Welcome back")


class PagesAppConfigTests(TestCase):
    def test_apps_config(self):
        from django.apps import apps
        config = apps.get_app_config("pages")
        self.assertEqual(config.name, "pages")
        self.assertEqual(config.verbose_name, "Pages")
