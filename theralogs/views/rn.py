import requests
from decouple import config
from django.http import JsonResponse
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.models import User


from theralogs.models import Patient, TLSession, Therapist
from ..tasks import create_transcribe
from ..utils import read_file


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)


class TherapistSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Therapist
        fields = ("id", "user", "name", "license_id", "city", "state", "created_at")


class MainView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        patients = []
        for p in request.user.therapist.patient_set.all():
            patients.append({"id": p.id, "name": p.name, "email": p.email})
        context = {"msg": "success", "patients": patients}
        return JsonResponse(context)


class AudioUploadView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        patient_id = request.POST.get("patient-id")
        patient = Patient.objects.get(id=patient_id)

        my_file = request.FILES.get("file")
        tl_session = TLSession(patient=patient, recording_length=0)
        tl_session.save()

        headers = {"authorization": config("ASSEMBLY_AI_KEY")}
        response = requests.post(
            "https://api.assemblyai.com/v2/upload",
            headers=headers,
            data=read_file(my_file.temporary_file_path()),
        )

        json_response = response.json()
        upload_url = json_response["upload_url"]

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
        context = {"msg": "success"}
        return JsonResponse(context)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        serializer = TherapistSerializer(request.user.therapist)
        return Response(serializer.data)
