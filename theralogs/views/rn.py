from django.http import JsonResponse
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from theralogs.models import Patient, TLSession
from ..managers.audio_transcribe_manager import audio_transcribe_manager
from ..serializers import TherapistSerializer, TLSessionSerializer
from ..tasks import create_transcribe, resend_email_to_patient


class MainView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        patients = []
        for p in request.user.therapist.patient_set.all():
            patients.append({"id": p.id, "name": p.name, "email": p.email})
        return JsonResponse({"msg": "success", "patients": patients})


class AudioUploadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        patient_id = request.POST.get("patient-id")
        patient = Patient.objects.get(id=patient_id)

        my_file = request.FILES.get("file")
        tl_session = TLSession(patient=patient, recording_length=0)
        tl_session.save()

        upload_url = audio_transcribe_manager.upload_audio_file(
            temp_file_path=my_file.temporary_file_path()
        )

        task = create_transcribe.now(upload_url, tl_session.id)

        if task:
            return JsonResponse({"msg": "success"})
        return JsonResponse({"msg": "error"})


class CreatePatientView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        patient_name = request.POST.get("patient-name")
        patient_email = request.POST.get("patient-email")

        patient = Patient(
            name=patient_name, email=patient_email, therapist=request.user.therapist
        )
        patient.save()
        return JsonResponse({"msg": "success"})


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = TherapistSerializer(request.user.therapist)
        return Response(serializer.data)


class ClientProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, patient_id):
        patient = Patient.objects.get(id=patient_id)
        if patient:
            sessions = patient.tlsession_set.all()
            serializer = TLSessionSerializer(sessions, many=True)
            return Response(serializer.data)
        return JsonResponse({"msg": "error"})


class ResendSessionPDFView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, session_id):
        task = resend_email_to_patient.now(str(session_id))
        return JsonResponse({"msg": "success"})
