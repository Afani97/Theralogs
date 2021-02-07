import json
from collections import OrderedDict
from datetime import datetime

import dateutil.relativedelta
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from ..managers.audio_transcribe_manager import audio_transcribe_manager
from ..models import Patient, TLSession
from ..tasks import (
    send_email_transcript,
    resend_email_to_patient,
    create_transcribe,
)


class LandingPage(TemplateView):
    template_name = "theralogs/landing_page.html"


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
        tl_session = TLSession(patient=patient, recording_length=0)
        tl_session.save()

        upload_url = audio_transcribe_manager.upload_audio_file(
            temp_file_path=my_file.temporary_file_path()
        )

        task = create_transcribe.now(upload_url, str(tl_session.id))

        if task:
            return JsonResponse({"msg": "success"})

    return JsonResponse({"msg": "error"})


@login_required
def resend_email(request, session_id):
    task = resend_email_to_patient.now(str(session_id))
    return JsonResponse({"msg": "success"})


@csrf_exempt
def transcribe_webhook(request):
    session_id = request.GET.getlist("session_id")[0]
    session = TLSession.objects.get(id=session_id)
    if session:
        payload = json.loads(request.body.decode("utf-8"))
        status = payload["status"]
        if status == "completed":
            transcript_id = payload["transcript_id"]
            send_email_transcript.now(str(session_id), transcript_id)
        else:
            print("Error transcribing text")
    else:
        print("Session not found")
    return HttpResponse("OK")
