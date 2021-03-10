import uuid

import mock
from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from theralogs.models import Therapist


class TestProfileViews(TestCase):
    def setUp(self):
        user = User.objects.create(username="therapist@test.com")
        user.email = "therapist@test.com"
        user.set_password("Apple101!")
        user.save()

        user = User.objects.get(email="therapist@test.com")
        self.therapist = Therapist.objects.create(
            name="Tom", user=user, stripe_customer_id=str(uuid.uuid4())
        )
        self.client = Client()

    def test_view_profile(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.get(reverse("profile"))
        self.assertEquals(response.status_code, 200)

    def test_view_profile_failed(self):
        response = self.client.get(reverse("profile"))
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, "/login/?next=/profile/")

    def test_edit_profile(self):
        self.client.login(username="therapist@test.com", password="Apple101!")

        response = self.client.post(
            reverse("edit_profile"),
            {
                "name": "Tom",
                "email": "therapist@test.com",
                "license_id": str(uuid.uuid4()),
                "city": "Worcester",
                "state": "MA",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("profile"))

    def test_edit_profile_failed(self):
        second_user = User.objects.create(username="therapist2@test.com")
        second_user.email = "therapist2@test.com"
        second_user.set_password("Apple101!")
        second_user.save()

        second_user = User.objects.filter(email="therapist2@test.com").first()
        second_therapist = Therapist.objects.create(
            name="Tom 2", user=second_user, stripe_customer_id=str(uuid.uuid4())
        )
        self.client.login(username="therapist@test.com", password="Apple101!")

        response = self.client.put(
            reverse("edit_profile"),
            {
                "name": "Tom",
                "email": second_therapist.user.email,
                "license_id": str(uuid.uuid4()),
                "city": "Worcester",
                "state": "MA",
            },
        )
        self.assertEquals(response.status_code, 200)
        therapist = Therapist.objects.get(id=self.therapist.id)
        self.assertEquals(therapist.user.email, "therapist@test.com")
        self.assertNotEquals(therapist.user.email, second_user.email)

    @mock.patch("stripe.PaymentMethod.create")
    @mock.patch("stripe.PaymentMethod.detach")
    @mock.patch("stripe.PaymentMethod.attach")
    @mock.patch("stripe.Customer.modify")
    def test_profile_payment_update(
        self, modify_mock, attach_mock, detach_mock, create_mock
    ):
        self.client.login(username="therapist@test.com", password="Apple101!")
        create_mock.return_value = {"id": str(uuid.uuid4())}
        detach_mock.return_value = {}
        attach_mock.return_value = {}
        modify_mock.return_value = {}
        response = self.client.post(
            reverse("update_payment"),
            {
                "card_number": "4242424242424242",
                "card_exp_month": 8,
                "card_exp_year": 2025,
                "card_cvc": "123",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("profile"))

    def test_profile_payment_update_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("update_payment"),
            {
                "number": "4242424242424242",
            },
        )
        self.assertEquals(response.status_code, 400)

    def test_delete_profile(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("delete_profile"),
            {
                "confirm_password": "Apple101!",
            },
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("login"))

        therapist = Therapist.objects.filter(id=self.therapist.id).first()
        self.assertEquals(therapist, None)

    def test_delete_patient_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("delete_profile"),
            {
                "confirm_password": "wrong_password",
            },
        )
        self.assertEquals(response.status_code, 400)
