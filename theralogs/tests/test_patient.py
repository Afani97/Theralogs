import uuid

from django.contrib.auth.models import User
from django.test import TestCase, Client
from django.urls import reverse

from theralogs.models import Therapist, Patient


class TestPatientViews(TestCase):
    def setUp(self):
        user = User.objects.create(username="therapist@test.com")
        user.set_password("Apple101!")
        user.save()

        user = User.objects.get(username="therapist@test.com")
        self.therapist = Therapist.objects.create(
            name="Tom", user=user, stripe_customer_id=str(uuid.uuid4())
        )
        self.client = Client()

    def test_create_patient(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("patient_create"),
            {"name": "Jane", "email": "jane@test.com"},
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("profile"))

    def test_create_patient_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("patient_create"),
            {"name": "Jane"},
        )
        self.assertEquals(response.status_code, 400)

    def test_create_patient_ajax(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("patient_create"),
            {"patient-name": "Jane", "patient-email": "jane@test.com"},
            **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        )
        self.assertEquals(response.status_code, 200)

    def test_create_patient_ajax_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("patient_create"),
            {"patient-name": "Jane"},
            **{"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}
        )
        self.assertEquals(response.status_code, 400)

    def test_edit_patient(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        patient = Patient.objects.create(
            name="Jane", email="jane@test.com", therapist=self.therapist
        )
        response = self.client.post(
            reverse("patient_edit", kwargs={"patient_id": patient.id}),
            {"name": "Jane 2", "email": "jane@test.com"},
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("profile"))

        patient = Patient.objects.get(id=patient.id)
        self.assertEquals(patient.name, "Jane 2")

    def test_edit_patient_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        patient = Patient.objects.create(
            name="Jane", email="jane@test.com", therapist=self.therapist
        )
        response = self.client.post(
            reverse("patient_edit", kwargs={"patient_id": patient.id}),
            {"name": "Jane 2"},
        )
        self.assertEquals(response.status_code, 400)

    def test_delete_patient(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        patient = Patient.objects.create(
            name="Jane", email="jane@test.com", therapist=self.therapist
        )
        response = self.client.post(
            reverse("patient_delete", kwargs={"patient_id": patient.id})
        )
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.url, reverse("profile"))

        patient = Patient.objects.filter(id=patient.id).first()
        self.assertEquals(patient, None)

    def test_delete_patient_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("patient_delete", kwargs={"patient_id": uuid.uuid4()})
        )
        self.assertEquals(response.status_code, 400)
