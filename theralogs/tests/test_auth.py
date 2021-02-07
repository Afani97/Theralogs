import uuid
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from theralogs.models import Therapist
import mock


class TestAuthViews(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="therapist@test.com",
            email="therapist@test.com",
            password="Apple101!",
        )
        user = User.objects.get(username="therapist@test.com")
        Therapist.objects.create(
            name="Tom", user=user, stripe_customer_id=str(uuid.uuid4())
        )

    def test_login(self):
        client = Client()
        response = client.post(
            reverse("login"), {"email": "therapist@test.com", "password": "Apple101!"}
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("home"))

    def test_login_failed(self):
        client = Client()
        response = client.post(
            reverse("login"), {"email": "therapist@test.com", "password": "Apple101"}
        )
        self.assertEquals(response.status_code, 400)

    @mock.patch("stripe.Customer.create")
    def test_signup(self, create_mock):
        client = Client()
        create_mock.return_value = {"id": str(uuid.uuid4())}
        response = client.post(
            reverse("signup"),
            {
                "first_name": "Thomas",
                "email": "thomas@test.com",
                "password1": "Apple101!",
                "password2": "Apple101!",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("home"))

    @mock.patch("stripe.Customer.create")
    def test_signup_error(self, create_mock):
        client = Client()
        create_mock.return_value = {"id": str(uuid.uuid4())}
        response = client.post(
            reverse("signup"),
            {
                "first_name": "Thomas",
                "email": "thomas2@test.com",
                "password1": "Apple101!",
            },
        )
        self.assertEquals(response.status_code, 400)

    def test_logout(self):
        client = Client()
        client.post(
            reverse("login"), {"email": "therapist@test.com", "password": "Apple101"}
        )

        response = client.get(reverse("logout"))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login/?next=/logout/")

    def test_logout_failed_redirect(self):
        client = Client()
        response = client.get(reverse("logout"))

        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login/?next=/logout/")
