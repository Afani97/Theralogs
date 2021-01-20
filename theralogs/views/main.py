import json
from collections import OrderedDict
from datetime import datetime

import dateutil.relativedelta
import mutagen
import requests
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from theralogsproject.storage_backends import MediaStorage
from ..models import TLFile, Patient, TLSession
from ..tasks import generate_transcribe, send_email_transcript, resend_email_to_patient


@login_required
def main_view(request, filter_date=None):
    therapist = request.user.therapist
    patients = therapist.patient_set.all()

    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year
    sessions_by_date = {}

    if filter_date:
        current_month = int(filter_date.split("-")[0])
        current_year = int(filter_date.split("-")[1])

    for patient in patients:
        sessions = patient.tlsession_set.filter(created_at__month=current_month).filter(
            created_at__year=current_year
        )
        for s in sessions:
            session_date = s.created_at.date()
            if session_date in sessions_by_date.keys():
                current_sessions = sessions_by_date[session_date]
                current_sessions.append(s)
                sessions_by_date[session_date] = current_sessions
            else:
                sessions_by_date[session_date] = [s]

    ordered_sessions = OrderedDict(sorted(sessions_by_date.items(), key=lambda t: t[0]))

    if filter_date:
        date_str = f"01/{current_month}/{current_year}"
        format_str = "%d/%m/%Y"
        current_date = datetime.strptime(date_str, format_str).date()

    prev_month = current_date + dateutil.relativedelta.relativedelta(months=-1)
    next_month = current_date + dateutil.relativedelta.relativedelta(months=1)

    context = {
        "patients": patients,
        "sessions": ordered_sessions,
        "prev_month": f"{prev_month.month}-{prev_month.year}",
        "curr_month": current_date,
        "next_month": f"{next_month.month}-{next_month.year}",
    }
    return render(request, "theralogs/mainview.html", context)


@login_required
def file_upload(request):
    if request.method == "POST":
        patient_id = request.POST.get("patient-id")
        patient = Patient.objects.get(id=patient_id)

        my_file = request.FILES.get("file")
        audio_file = mutagen.File(my_file.temporary_file_path())
        tl_session = TLSession(patient=patient, recording_length=audio_file.info.length)
        tl_session.save()

        my_file.name = f"{tl_session.id}"

        TLFile.objects.create(file=my_file)

        media_storage = MediaStorage()
        file_uri = media_storage.url(my_file.name)
        task = generate_transcribe.delay(my_file.name, file_uri)

        if task:
            return JsonResponse({"msg": "success"})

    return JsonResponse({"msg": "error"})


@login_required
def resend_email(request, session_id):
    task = resend_email_to_patient.delay(session_id)
    return JsonResponse({"msg": "success"})


@csrf_exempt
def sns_transcribe_event(request):
    message_type_header = "HTTP_X_AMZ_SNS_MESSAGE_TYPE"
    if message_type_header in request.META:
        payload = json.loads(request.body.decode("utf-8"))

        message_type = request.META[message_type_header]
        if message_type == "SubscriptionConfirmation":
            subscribe_url = payload.get("SubscribeURL")
            res = requests.get(subscribe_url)
            if res.status_code != 200:
                return HttpResponse(
                    "Invalid verification:\n{0}".format(res.content), status=400
                )
        else:
            payload = json.loads(request.body.decode("utf-8"))
            message = json.loads(payload["Message"])
            job_name = message["detail"]["TranscriptionJobName"].split("@")[0]
            task = send_email_transcript.delay(job_name)

    return HttpResponse("OK")
