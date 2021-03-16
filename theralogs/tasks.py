from background_task import background

from theralogs.managers.audio_transcribe_manager import audio_transcribe_manager
from theralogs.managers.email_manager import email_manager
from theralogs.managers.stripe_manager import stripe_manager
from theralogs.models import TLSession
from theralogsproject.settings import DEBUG


class background_tasks:
    @staticmethod
    @background(schedule=60)
    def create_transcribe(upload_url, session_id):
        webhook_base = "https://9af27751b97b.ngrok.io"
        if not DEBUG:
            webhook_base = "https://www.usetheralogs.com"
        task = audio_transcribe_manager.upload_audio_url(
            webhook_base=webhook_base, upload_url=upload_url, session_id=session_id
        )
        return task

    @staticmethod
    @background(schedule=60)
    def send_email_transcript(session_id, transcript_id):
        session = TLSession.objects.get(id=session_id)
        session.transcript_id = transcript_id
        session.save()

        response_json = audio_transcribe_manager.get_transcript(
            transcript_id=session.transcript_id
        )

        audio_duration = float(response_json["audio_duration"])
        session.recording_length = audio_duration
        session.save()

        total_minutes_of_recording = session.recording_length / 60
        refund_id = stripe_manager.charge_customer(
            recording_time=total_minutes_of_recording, patient=session.patient
        )
        if refund_id:
            session.stripe_refund_id = refund_id
            session.progress = TLSession.ProgressTypes.COMPLETED
            session.save()

            email_manager.send_email(session=session)
            return True
        else:
            session.progress = TLSession.ProgressTypes.FAILED
            session.save()
            return False

    @staticmethod
    @background(schedule=60)
    def resend_email_to_patient(session_id):
        session = TLSession.objects.get(id=session_id)
        email_manager.send_email(session=session)
        return True

    @staticmethod
    @background(schedule=60)
    def send_contact_us(name, email, question):
        email_dict = {"name": name, "email": email, "question": question}
        email_manager.send_contact_us_email(dict=email_dict)
        return True

    @staticmethod
    @background(schedule=60)
    def send_new_customer(name, email):
        email_dict = {"name": name, "email": email}
        email_manager.send_new_customer_notification(dict=email_dict)
        return True
