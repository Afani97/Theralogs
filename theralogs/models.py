import uuid
from django_cryptography.fields import encrypt

from django.contrib.auth.models import User
from django.db import models


class Account(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False, blank=False)
    name = encrypt(models.CharField(max_length=200, null=False))
    created_at = models.DateTimeField(auto_now_add=True)
    stripe_customer_id = encrypt(
        models.CharField(max_length=200, null=False, blank=False, editable=False)
    )
    stripe_payment_method_id = encrypt(
        models.CharField(max_length=200, null=True, blank=True, editable=False)
    )

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Therapist(Account):
    license_id = encrypt(models.CharField(max_length=200, null=False, blank=False))
    city = encrypt(models.CharField(max_length=200, null=False, blank=False))
    state = encrypt(models.CharField(max_length=200, null=False, blank=False))


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    name = encrypt(models.CharField(max_length=200, null=False))
    email = encrypt(models.EmailField(null=False))

    def __str__(self):
        return self.name


class TLSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    recording_json = encrypt(models.TextField(blank=True, null=True, editable=False))
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    recording_length = models.FloatField()

    def __str__(self):
        return str(self.id)
