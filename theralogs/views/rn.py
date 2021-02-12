from django.http import JsonResponse, HttpResponse
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from theralogs.models import Patient, TLSession
from ..managers.audio_transcribe_manager import audio_transcribe_manager
from ..serializers import TherapistSerializer, TLSessionSerializer
from ..tasks import background_tasks


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

                task = background_tasks.create_transcribe(upload_url, tl_session.id)

                if task:
                    return JsonResponse({"msg": "success"})
        return JsonResponse({"msg": "error"}, status=400)


class CreatePatientView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        patient_name = request.POST.get("patient-name")
        patient_email = request.POST.get("patient-email")
        if patient_email and patient_name:
            patient = Patient(
                name=patient_name, email=patient_email, therapist=request.user.therapist
            )
            patient.save()
            return JsonResponse({"msg": "success"})
        else:
            return Response({"msg": "error"}, status=status.HTTP_400_BAD_REQUEST)


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
        if session_id:
            session = TLSession.objects.filter(id=session_id).exists()
            if session:
                task = background_tasks.resend_email_to_patient(str(session_id))
                if task:
                    return JsonResponse({"msg": "success"})
        return JsonResponse({"msg": "error"}, status=400)
