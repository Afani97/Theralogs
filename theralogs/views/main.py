import json
from datetime import datetime

import dateutil.relativedelta
from csp.decorators import csp_exempt
from django.contrib.auth.decorators import login_required
from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from ..managers.audio_transcribe_manager import audio_transcribe_manager
from ..models import Patient, TLSession
from ..tasks import background_tasks
from ..utils import render_to_pdf, format_transcript_utterances, format_date


class LandingPage(TemplateView):
    template_name = "theralogs/landing_page.html"


@login_required
def main_view(request, filter_date=None):
    current_date = datetime.now()
    current_month = current_date.month
    current_year = current_date.year

    if filter_date:
        current_month = int(filter_date.split("-")[0])
        current_year = int(filter_date.split("-")[1])
        current_date = format_date(current_month, current_year)

    ordered_sessions = request.user.therapist.get_sessions(current_month, current_year)

    prev_month = current_date + dateutil.relativedelta.relativedelta(months=-1)
    next_month = current_date + dateutil.relativedelta.relativedelta(months=1)

    context = {
        "patients": request.user.therapist.patient_set.all(),
        "sessions": ordered_sessions,
        "prev_month": f"{prev_month.month}-{prev_month.year}",
        "curr_month": current_date,
        "next_month": f"{next_month.month}-{next_month.year}",
    }
    return render(request, "theralogs/mainview.html", context)


@login_required
def file_upload(request):
    if request.method == "POST":
        if request.user.therapist.stripe_payment_method_id:
            patient_id = request.POST.get("patient-id")
            patient = Patient.objects.get(id=patient_id)

            my_file = request.FILES.get("file")
            if my_file:
                tl_session = TLSession(patient=patient, recording_length=0)
                tl_session.save()

                upload_url = audio_transcribe_manager.upload_audio_file(
                    temp_file_path=my_file.temporary_file_path()
                )

                task = background_tasks.create_transcribe(
                    upload_url, str(tl_session.id)
                )

                if task:
                    return JsonResponse({"msg": "success"})

    return JsonResponse({"msg": "error"}, status=400)


@login_required
@csp_exempt
def view_pdf(request, session_id):
    if session_id:
        try:
            session = TLSession.objects.filter(id=session_id).first()
        except TLSession.DoesNotExist:
            session = None
        if session and session.transcript_id:
            response_json = audio_transcribe_manager.get_transcript(
                transcript_id=session.transcript_id
            )

            utterances = response_json["utterances"]
            formatted_transcript = format_transcript_utterances(utterances)

            context = {
                "transcript": formatted_transcript,
                "date_created": session.created_at,
            }

            pdf = render_to_pdf(context)
            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = "inline;filename=transcript.pdf"
            return response
    return redirect(reverse("home"))


@login_required
def resend_email(request, session_id):
    if session_id:
        session = TLSession.objects.filter(id=session_id).exists()
        if session:
            task = background_tasks.resend_email_to_patient(str(session_id))
            if task:
                return JsonResponse({"msg": "success"})
    return JsonResponse({"msg": "error"}, status=400)


@csrf_exempt
def transcribe_webhook(request):
    if request.GET.getlist("session_id"):
        session_id = request.GET.getlist("session_id")[0]
        session = TLSession.objects.filter(id=session_id).exists()
        if session:
            payload = json.loads(request.body.decode("utf-8"))
            status = payload["status"]
            if status == "completed":
                transcript_id = payload["transcript_id"]
                task = background_tasks.send_email_transcript(
                    str(session_id), transcript_id
                )
                if task:
                    return HttpResponse("Ok")
            else:
                session = TLSession.objects.get(id=session_id)
                session.progress = TLSession.ProgressTypes.FAILED
                session.save()
    return HttpResponseBadRequest("Session not found")
