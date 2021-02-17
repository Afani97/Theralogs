"""theralogsproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django_otp.admin import OTPAdminSite
from django.contrib import admin, messages
from django.contrib.auth.models import User
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.plugins.otp_totp.admin import TOTPDeviceAdmin
from theralogs.models import TLSession, Therapist, Patient


class OTPAdmin(OTPAdminSite):
    pass


admin_site = OTPAdmin(name="OTPAdmin")
admin_site.register(User)
admin_site.register(TOTPDevice, TOTPDeviceAdmin)


# Register your models here.
admin_site.register(Therapist)
admin_site.register(Patient)


def refund_charge(modeladmin, request, queryset):
    for session in queryset:
        refunded = session.refund_charge()
        print(refunded)
        if refunded is True:
            messages.add_message(request, messages.WARNING, "Session already refunded")
        elif refunded is False:
            messages.add_message(request, messages.SUCCESS, "Session has been refunded")
            session.refunded = True
            session.save()
        else:
            messages.add_message(
                request, messages.ERROR, "Session unable to be refunded"
            )


refund_charge.short_description = "Refund session"


class TLSessionAdmin(admin.ModelAdmin):
    list_display = ["id", "created_at"]
    actions = [
        refund_charge,
    ]


admin_site.register(TLSession, TLSessionAdmin)


from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [path("admin/", admin_site.urls), path("", include("theralogs.urls"))]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
