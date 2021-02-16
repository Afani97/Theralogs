import uuid

import mock
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APIClient

from ..managers import audio_transcribe_manager
from theralogs.models import Therapist, Patient, TLSession
from theralogs.tasks import background_tasks


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
        self.patient = Patient.objects.create(
            name="Tom", email="tom@test.com", therapist=self.therapist
        )
        self.session = TLSession.objects.create(
            patient=self.patient, recording_length=0
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

    @mock.patch.object(
        audio_transcribe_manager.audio_transcribe_manager, "upload_audio_file"
    )
    @mock.patch.object(background_tasks, "create_transcribe")
    def test_file_upload(self, transcribe_mock, audio_file_mock):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        self.therapist.stripe_payment_method_id = f"{uuid.uuid4()}"
        self.therapist.save()

        audio_file_mock.return_value = "https://example.com/url"
        transcribe_mock.return_value = True

        simple_file = SimpleUploadedFile(
            "transcribe.mp4",
            b"file_content",
            content_type="video/mp4",
        )
        response = api_client.post(
            reverse("rn_file_upload"),
            {"patient-id": self.patient.id, "file": simple_file},
        )
        self.assertEquals(response.status_code, 200)

    @mock.patch.object(
        audio_transcribe_manager.audio_transcribe_manager, "upload_audio_file"
    )
    @mock.patch.object(background_tasks, "create_transcribe")
    def test_file_upload_no_stripe_payment_failed(
        self, transcribe_mock, audio_file_mock
    ):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        audio_file_mock.return_value = "https://example.com/url"
        transcribe_mock.return_value = True

        simple_file = SimpleUploadedFile(
            "transcribe.mp4",
            b"file_content",
            content_type="video/mp4",
        )
        response = api_client.post(
            reverse("rn_file_upload"),
            {"patient-id": self.patient.id, "file": simple_file},
        )
        self.assertEquals(response.status_code, 400)

    def test_file_upload_error(self):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        response = api_client.post(
            reverse("rn_file_upload"), {"patient-id": self.patient.id}
        )
        self.assertEquals(response.status_code, 400)

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

    @mock.patch.object(background_tasks, "resend_email_to_patient")
    def test_resend_session(self, send_email_mock):
        send_email_mock.return_value = True
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        response = api_client.get(
            reverse("rn_resend_email", kwargs={"session_id": self.session.id})
        )
        self.assertEquals(response.status_code, 200)

    def test_resend_session_failed(self):
        api_client = APIClient()
        api_client.credentials(HTTP_AUTHORIZATION="Bearer " + self.token)

        response = api_client.get(
            reverse("rn_resend_email", kwargs={"session_id": uuid.uuid4()})
        )
        self.assertEquals(response.status_code, 400)
