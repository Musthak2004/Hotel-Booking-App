from django.test import TestCase
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model

from .models import CustomUser, Profile
from .forms import CustomUserRegistrationForm, CustomUserUpdateForm, ProfileUpdateForm
from .views import SignUpView

User = get_user_model()


class CustomUserModelTests(TestCase):
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123",
        )
        self.assertEqual(user.email, "test@example.com")
        self.assertEqual(user.username, "testuser")
        self.assertTrue(user.check_password("testpass123"))
        self.assertEqual(user.role, "customer")

    def test_create_user_with_custom_role(self):
        user = User.objects.create_user(
            username="owner1",
            email="owner@example.com",
            password="testpass123",
            role="owner",
        )
        self.assertEqual(user.role, "owner")

    def test_email_is_unique(self):
        User.objects.create_user(
            username="user1", email="same@example.com", password="pass"
        )
        with self.assertRaises(Exception):
            User.objects.create_user(
                username="user2", email="same@example.com", password="pass"
            )

    def test_string_representation(self):
        user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass"
        )
        self.assertEqual(str(user), "test@example.com")

    def test_username_is_required(self):
        with self.assertRaises(TypeError):
            User.objects.create_user(email="test@example.com", password="pass")


class ProfileModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="pass"
        )

    def test_profile_auto_created_on_user_creation(self):
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_profile_one_to_one_relationship(self):
        profile = self.user.profile
        self.assertEqual(profile.user, self.user)

    def test_profile_string_representation(self):
        self.assertEqual(str(self.user.profile), "test@example.com")

    def test_profile_default_fields_are_blank(self):
        profile = self.user.profile
        self.assertEqual(profile.address, "")
        self.assertEqual(profile.city, "")
        self.assertEqual(profile.country, "")
        self.assertEqual(profile.postal_code, "")


class SignupFormTests(TestCase):
    def test_registration_form_valid_data(self):
        form = CustomUserRegistrationForm(data={
            "username": "newuser",
            "email": "new@example.com",
            "phone_number": "1234567890",
            "role": "customer",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        })
        self.assertTrue(form.is_valid())

    def test_registration_form_missing_email(self):
        form = CustomUserRegistrationForm(data={
            "username": "newuser",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_registration_form_password_mismatch(self):
        form = CustomUserRegistrationForm(data={
            "username": "newuser",
            "email": "new@example.com",
            "password1": "strongpassword123",
            "password2": "differentpassword456",
        })
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_registration_form_saves_user(self):
        form = CustomUserRegistrationForm(data={
            "username": "newuser",
            "email": "new@example.com",
            "phone_number": "1234567890",
            "role": "customer",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        })
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.email, "new@example.com")
        self.assertTrue(user.check_password("strongpassword123"))

    def test_update_form_valid(self):
        form = CustomUserUpdateForm(data={
            "username": "updateduser",
            "email": "updated@example.com",
            "phone_number": "0987654321",
        })
        self.assertTrue(form.is_valid())

    def test_profile_update_form_valid(self):
        form = ProfileUpdateForm(data={
            "address": "123 Main St",
            "city": "New York",
            "country": "USA",
            "postal_code": "10001",
        })
        self.assertTrue(form.is_valid())


class SignUpViewTests(TestCase):
    def test_signup_url_resolves_to_signup_view(self):
        match = resolve("/accounts/signup/")
        self.assertEqual(match.func.view_class, SignUpView)

    def test_signup_url_name(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)

    def test_signup_uses_correct_template(self):
        response = self.client.get(reverse("signup"))
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_creates_user(self):
        response = self.client.post(reverse("signup"), data={
            "username": "newuser",
            "email": "new@example.com",
            "phone_number": "1234567890",
            "role": "customer",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.assertTrue(User.objects.filter(email="new@example.com").exists())

    def test_signup_creates_profile_via_signal(self):
        self.client.post(reverse("signup"), data={
            "username": "newuser",
            "email": "new@example.com",
            "phone_number": "1234567890",
            "role": "customer",
            "password1": "strongpassword123",
            "password2": "strongpassword123",
        })
        user = User.objects.get(email="new@example.com")
        self.assertTrue(Profile.objects.filter(user=user).exists())

    def test_signup_invalid_data_returns_form(self):
        response = self.client.post(reverse("signup"), data={
            "username": "",
            "email": "invalid-email",
            "password1": "pass",
            "password2": "mismatch",
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")


class SignalTests(TestCase):
    def test_profile_created_on_user_creation(self):
        self.assertEqual(Profile.objects.count(), 0)
        User.objects.create_user(
            username="testuser", email="test@example.com", password="pass"
        )
        self.assertEqual(Profile.objects.count(), 1)

    def test_profile_created_for_each_user(self):
        User.objects.create_user(
            username="user1", email="user1@example.com", password="pass"
        )
        User.objects.create_user(
            username="user2", email="user2@example.com", password="pass"
        )
        self.assertEqual(Profile.objects.count(), 2)


class URLTests(TestCase):
    def test_home_url_resolves(self):
        match = resolve("/")
        self.assertEqual(match.url_name, "home")

    def test_signup_url_resolves(self):
        match = resolve("/accounts/signup/")
        self.assertEqual(match.url_name, "signup")

    def test_login_url_resolves(self):
        match = resolve("/accounts/login/")
        self.assertEqual(match.url_name, "login")

    def test_logout_url_resolves(self):
        match = resolve("/accounts/logout/")
        self.assertEqual(match.url_name, "logout")
