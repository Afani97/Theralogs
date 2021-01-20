import json

import boto3
from botocore.config import Config
from celery import shared_task

from theralogs.email_manager import email_manager
from theralogs.models import TLSession, Patient
from theralogs.stripe_manager import stripe_manager
from theralogs.utils import format_transcript
from theralogsproject.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


@shared_task
def generate_transcribe(file_name, file_uri):
    my_config = Config(region_name="us-east-1")
    transcribe = boto3.client(
        "transcribe",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=my_config,
    )
    job_name = f"{file_name}-medical"
    try:
        transcribe.start_medical_transcription_job(
            MedicalTranscriptionJobName=job_name,
            Media={"MediaFileUri": file_uri},
            LanguageCode="en-US",
            Specialty="PRIMARYCARE",
            Type="CONVERSATION",
            OutputBucketName="aristotel-dev-theralogs",
            Settings={"ShowSpeakerLabels": True, "MaxSpeakerLabels": 2},
        )
    except:
        return None
    return True


@shared_task
def send_email_transcript(job_name):
    patient_session_id = job_name.split("-medical")[0]
    patient_session = TLSession.objects.get(id=patient_session_id)
    patient = Patient.objects.get(id=patient_session.patient.id)
    my_config = Config(region_name="us-east-1")
    s3 = boto3.resource(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        config=my_config,
    )
    obj = s3.Object("aristotel-dev-theralogs", f"medical/{job_name}.json")
    file_content = obj.get()["Body"].read().decode("utf-8")
    json_content = json.loads(file_content)
    formatted_transcript = format_transcript(json_content)

    context = {"transcript": formatted_transcript}
    patient_session.recording_json = context
    patient_session.save()

    total_minutes_of_recording = patient_session.recording_length / 60
    stripe_manager.charge_customer(
        recording_time=total_minutes_of_recording, patient=patient
    )

    email_manager.send_email(session=patient_session)

    return True


@shared_task
def resend_email_to_patient(session_id):
    session = TLSession.objects.get(id=session_id)

    email_manager.send_email(session=session)

    return True
