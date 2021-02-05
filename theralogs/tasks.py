import json

from background_task import background

from theralogs.managers.audio_transcribe_manager import audio_transcribe_manager
from theralogs.managers.email_manager import email_manager
from theralogs.managers.stripe_manager import stripe_manager
from theralogs.models import TLSession
from theralogs.utils import format_transcript_utterances
from theralogsproject.settings import DEBUG


@background(schedule=5)
def create_transcribe(upload_url, session_id):
    webhook_base = "http://63c562dd4fdf.ngrok.io"
    if not DEBUG:
        webhook_base = "https://www.usetheralogs.com"
    task = audio_transcribe_manager.upload_audio_url(
        webhook_base=webhook_base, upload_url=upload_url, session_id=session_id
    )
    return task


@background(schedule=5)
def send_email_transcript(session_id, transcript_id):
    session = TLSession.objects.get(id=session_id)

    response_json = audio_transcribe_manager.get_transcript(transcript_id=transcript_id)

    audio_duration = float(response_json["audio_duration"])
    session.recording_length = audio_duration

    utterances = response_json["utterances"]
    formatted_transcript = format_transcript_utterances(utterances)
    context = json.dumps(formatted_transcript)
    session.recording_json = context
    session.save()

    total_minutes_of_recording = session.recording_length / 60
    stripe_manager.charge_customer(
        recording_time=total_minutes_of_recording, patient=session.patient
    )

    email_manager.send_email(session=session)

    return True


@background(schedule=5)
def resend_email_to_patient(session_id):
    session = TLSession.objects.get(id=session_id)
    email_manager.send_email(session=session)
    return True
