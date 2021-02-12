from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from theralogs.models import TLSession, Therapist


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super(CustomTokenObtainPairSerializer, self).validate(attrs)
        data.update(
            {
                "stripe_verified": self.user.therapist.stripe_payment_method_id
                is not None
            }
        )
        return data


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
