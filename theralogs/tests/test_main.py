import json
import uuid
from datetime import datetime

import dateutil
import mock
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.urls import reverse

from ..managers import audio_transcribe_manager
from ..tasks import background_tasks
from theralogs.models import Therapist, Patient, TLSession


class TestMainViews(TestCase):
    def setUp(self):
        user = User.objects.create(username="therapist@test.com")
        user.set_password("Apple101!")
        user.save()

        user = User.objects.get(username="therapist@test.com")
        self.therapist = Therapist.objects.create(
            name="Tom", user=user, stripe_customer_id=str(uuid.uuid4())
        )

        self.patient = Patient.objects.create(
            name="Jane", email="jane@test.com", therapist=self.therapist
        )
        self.session = TLSession.objects.create(
            patient=self.patient, recording_length=0
        )
        self.client = Client()

    def test_landing_page(self):
        response = self.client.get("")
        self.assertTemplateUsed(response, "theralogs/landing_page.html")

    def test_main_view(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["patients"].count(), 1)
        self.assertEquals(len(response.context["sessions"]), 1)

    def test_main_view_filter_date(self):
        self.client.login(username="therapist@test.com", password="Apple101!")

        next_month = datetime.now() + dateutil.relativedelta.relativedelta(months=1)
        filter_date_kw = f"{next_month.month}-{next_month.year}"
        response = self.client.get(
            reverse("filter_main", kwargs={"filter_date": filter_date_kw}),
        )

        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.context["patients"].count(), 1)
        self.assertEquals(len(response.context["sessions"]), 0)

    def test_main_view_failed(self):
        response = self.client.get(reverse("home"))
        self.assertEquals(response.status_code, 302)

    @mock.patch.object(
        audio_transcribe_manager.audio_transcribe_manager, "upload_audio_file"
    )
    @mock.patch.object(background_tasks, "create_transcribe")
    def test_file_upload(self, transcribe_mock, audio_file_mock):
        self.client.login(username="therapist@test.com", password="Apple101!")
        self.therapist.stripe_payment_method_id = f"{uuid.uuid4()}"
        self.therapist.save()

        audio_file_mock.return_value = "https://example.com/url"
        transcribe_mock.return_value = True

        simple_file = SimpleUploadedFile(
            "TheraLogs-transcribe-example.mp4",
            b"file_content",
            content_type="video/mp4",
        )
        response = self.client.post(
            reverse("file_upload"),
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
        self.client.login(username="therapist@test.com", password="Apple101!")

        audio_file_mock.return_value = "https://example.com/url"
        transcribe_mock.return_value = True

        simple_file = SimpleUploadedFile(
            "TheraLogs-transcribe-example.mp4",
            b"file_content",
            content_type="video/mp4",
        )
        response = self.client.post(
            reverse("file_upload"),
            {"patient-id": self.patient.id, "file": simple_file},
        )
        self.assertEquals(response.status_code, 400)

    def test_file_upload_error(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("file_upload"), {"patient-id": self.patient.id}
        )
        self.assertEquals(response.status_code, 400)

    @mock.patch.object(background_tasks, "resend_email_to_patient")
    def test_resend_email(self, resend_mock):
        resend_mock.return_value = True
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.get(
            reverse("resend_email", kwargs={"session_id": self.session.id})
        )
        self.assertEquals(response.status_code, 200)

    def test_resend_email_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.get(
            reverse("resend_email", kwargs={"session_id": uuid.uuid4()})
        )
        self.assertEquals(response.status_code, 400)

    @mock.patch.object(background_tasks, "send_email_transcript")
    def test_transcribe_webhook(self, send_email_mock):
        send_email_mock.return_value = True
        self.client.login(username="therapist@test.com", password="Apple101!")
        json_dict = {"status": "completed", "transcript_id": str(uuid.uuid4())}
        response = self.client.post(
            reverse("aai-webhook") + f"?session_id={self.session.id}",
            json.dumps(json_dict),
            content_type="application/json",
        )
        self.assertEquals(response.status_code, 200)

    @mock.patch.object(background_tasks, "send_email_transcript")
    def test_transcribe_webhook_not_complete_failed(self, send_email_mock):
        send_email_mock.return_value = True
        self.client.login(username="therapist@test.com", password="Apple101!")
        json_dict = {"status": "error", "transcript_id": str(uuid.uuid4())}
        response = self.client.post(
            reverse("aai-webhook") + f"?session_id={self.session.id}",
            json.dumps(json_dict),
            content_type="application/json",
        )
        self.assertEquals(response.status_code, 400)

    def test_transcribe_webhook_invalid_session_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(
            reverse("aai-webhook") + f"?session_id={uuid.uuid4()}"
        )
        self.assertEquals(response.status_code, 400)

    def test_transcribe_webhook_failed(self):
        self.client.login(username="therapist@test.com", password="Apple101!")
        response = self.client.post(reverse("aai-webhook"))
        self.assertEquals(response.status_code, 400)
