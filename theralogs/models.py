import uuid

from django.contrib.auth.models import User
from django.db import models

from django_cryptography.fields import encrypt


class Therapist(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    name = encrypt(models.CharField(max_length=200, null=False))
    license_id = encrypt(models.CharField(max_length=200, null=False, blank=False))
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_customer_id = models.CharField(
        max_length=200, null=False, blank=False, editable=False
    )
    stripe_payment_method_id = models.CharField(
        max_length=200, null=True, blank=True, editable=False
    )


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    name = encrypt(models.CharField(max_length=200, null=False))
    email = encrypt(models.EmailField(null=False))


class TLSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    recording_length = models.FloatField()
    transcript_id = models.CharField(
        max_length=200, null=True, blank=True, editable=False
    )
