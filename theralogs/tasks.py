import json

import requests
from decouple import config
from background_task import background

from theralogs.managers.email_manager import email_manager
from theralogs.models import TLSession
from theralogs.managers.stripe_manager import stripe_manager
from theralogs.utils import format_transcript_utterances
from theralogsproject.settings import DEBUG


@background(schedule=5)
def create_transcribe(upload_url, session_id):
    webhook_base = "http://f4e6baf28f2b.ngrok.io"
    if not DEBUG:
        webhook_base = "https://www.usetheralogs.com"
    endpoint = "https://api.assemblyai.com/v2/transcript"

    json_body = {
        "audio_url": upload_url,
        "webhook_url": f"{webhook_base}/main/aai-webhook?session_id={session_id}",
        "speaker_labels": True,
    }

    headers = {
        "authorization": config("ASSEMBLY_AI_KEY"),
        "content-type": "application/json",
    }

    response = requests.post(endpoint, json=json_body, headers=headers)
    return True


@background(schedule=5)
def send_email_transcript(session_id, transcript_id):
    session = TLSession.objects.get(id=session_id)
    endpoint = f"https://api.assemblyai.com/v2/transcript/{transcript_id}"

    headers = {
        "authorization": config("ASSEMBLY_AI_KEY"),
    }

    response = requests.get(endpoint, headers=headers)
    response_json = response.json()

    audio_duration = float(response_json["audio_duration"])
    session.recording_length = audio_duration
    session.save()

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
