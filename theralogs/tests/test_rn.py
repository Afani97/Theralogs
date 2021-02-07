import uuid

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from theralogs.models import Therapist, Patient


class TestRNViews(TestCase):
    def setUp(self):
        User.objects.create_user(
            username="therapist@test.com",
            email="therapist@test.com",
            password="Apple101!",
        )
        user = User.objects.get(username="therapist@test.com")
        self.therapist = Therapist.objects.create(
            name="Tom", user=user, stripe_customer_id=str(uuid.uuid4())
        )
        client = Client()
        response = client.post(
            reverse("token_obtain_pair"),
            {"username": "therapist@test.com", "password": "Apple101!"},
        )
        self.token = response.data["access"]

    def test_main_view(self):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = api_client.get(reverse("rn_main"))
        self.assertEquals(response.status_code, 200)

    def test_main_view_failed(self):
        api_client = APIClient()
        response = api_client.get(reverse("rn_main"))
        self.assertEquals(response.status_code, 401)

    def test_create_patient(self):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = api_client.post(
            reverse("rn_patient_create"),
            {"patient-name": "Tom", "patient-email": "tom@test.com"},
        )
        self.assertEquals(response.status_code, 200)

    def test_create_patient_failed(self):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = api_client.post(
            reverse("rn_patient_create"),
            {"patient-name": "Tom"},
        )
        self.assertEquals(response.status_code, 400)

    def test_profile_view(self):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        response = api_client.get(reverse("rn_profile"))
        self.assertEquals(response.status_code, 200)

    def test_profile_view_failed(self):
        api_client = APIClient()
        response = api_client.get(reverse("rn_profile"))
        self.assertEquals(response.status_code, 401)

    def test_get_patient_profile(self):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)
        patient = Patient.objects.create(
            name="Tom", email="tom@test.com", therapist=self.therapist
        )
        response = api_client.get(
            reverse("rn_patient_profile", kwargs={"patient_id": patient.id})
        )
        self.assertEquals(response.status_code, 200)

    def test_get_patient_profile_failed(self):
        api_client = APIClient()
        response = api_client.get(
            reverse("rn_patient_profile", kwargs={"patient_id": uuid.uuid4()})
        )
        self.assertEquals(response.status_code, 401)
