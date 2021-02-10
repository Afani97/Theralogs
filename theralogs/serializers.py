from rest_framework import serializers
from django.contrib.auth.models import User
from theralogs.models import TLSession, Therapist


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email",)


class TherapistSerializer(serializers.ModelSerializer):
    user = UserSerializer(required=True)

    class Meta:
        model = Therapist
        fields = ("id", "user", "name", "license_id", "created_at")


class TLSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TLSession
        fields = (
            "id",
            "created_at",
        )
