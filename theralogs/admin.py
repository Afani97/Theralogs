from django.contrib import admin
from .models import TLFile, TLSession, Therapist, Patient
# Register your models here.

admin.site.register(TLFile)
admin.site.register(TLSession)
admin.site.register(Therapist)
admin.site.register(Patient)
