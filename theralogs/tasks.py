from celery import shared_task

from theralogs.managers.aws_manager import aws_manager
from theralogs.managers.email_manager import email_manager
from theralogs.models import TLSession
from theralogs.managers.stripe_manager import stripe_manager


@shared_task
def generate_transcribe(file_name, file_uri):
    job_name = f"{file_name}-medical"
    transcribe_job = aws_manager.create_medical_transcript(
        job_name=job_name, file_uri=file_uri
    )
    if transcribe_job:
        return True
    return False


@shared_task
def send_email_transcript(job_name):
    patient_session_id = job_name.split("-medical")[0]
    patient_session = TLSession.objects.get(id=patient_session_id)
    if not patient_session:
        return False

    formatted_transcript = aws_manager.get_transcription_from_s3(job_name=job_name)
    context = {"transcript": formatted_transcript}
    patient_session.recording_json = context
    patient_session.save()

    total_minutes_of_recording = patient_session.recording_length / 60
    stripe_manager.charge_customer(
        recording_time=total_minutes_of_recording, patient=patient_session.patient
    )

    email_manager.send_email(session=patient_session)

    return True


@shared_task
def resend_email_to_patient(session_id):
    session = TLSession.objects.get(id=session_id)
    email_manager.send_email(session=session)
    return True
