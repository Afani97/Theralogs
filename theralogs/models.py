import uuid
from collections import OrderedDict

from django.contrib.auth.models import User
from django.db import models
from django_cryptography.fields import encrypt

from .managers.stripe_manager import stripe_manager


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

    def get_sessions(self, month, year):
        patients = self.patient_set.all()
        sessions_by_date = {}

        for patient in patients:
            sessions = patient.tlsession_set.filter(created_at__month=month).filter(
                created_at__year=year
            )
            for s in sessions:
                session_date = s.created_at.date()
                if session_date in sessions_by_date.keys():
                    current_sessions = sessions_by_date[session_date]
                    current_sessions.append(s)
                    sessions_by_date[session_date] = current_sessions
                else:
                    sessions_by_date[session_date] = [s]

        ordered_sessions = OrderedDict(
            sorted(sessions_by_date.items(), key=lambda t: t[0])
        )
        return ordered_sessions


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
    stripe_refund_id = models.CharField(
        max_length=200, null=True, blank=True, editable=False
    )
    refunded = models.BooleanField(default=False)

    def refund_charge(self):
        if self.refunded is False:
            return stripe_manager.refund_charge_session(self.stripe_refund_id)
        else:
            return True
