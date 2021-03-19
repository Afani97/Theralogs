from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.shortcuts import render
from ..models import TLSession, Therapist, Patient
from datetime import datetime


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


@staff_member_required
def view_analytics(request):
    therapist_count = Therapist.objects.count()
    patient_count = Patient.objects.count()
    current_date = datetime.now()
    sessions_today_count = (
        TLSession.objects.filter(created_at__year=current_date.year)
        .filter(created_at__month=current_date.month)
        .filter(created_at__day=current_date.day)
        .count()
    )
    total_hourly_session_for_month_annotate = (
        TLSession.objects.filter(created_at__year=current_date.year)
        .filter(created_at__month=current_date.month)
        .aggregate(session_seconds=Sum("recording_length"))
    )
    total_hourly_session_for_month = 0
    if total_hourly_session_for_month_annotate["session_seconds"]:
        total_hourly_session_for_month = (
            total_hourly_session_for_month_annotate["session_seconds"] / 3600
        )
    goal_hours_per_month = 2000
    percentage_to_goal = (total_hourly_session_for_month / goal_hours_per_month) * 100
    context = {
        "therapist_count": therapist_count,
        "patient_count": patient_count,
        "sessions_today_count": sessions_today_count,
        "total_session_hours": "{:.2f}".format(total_hourly_session_for_month),
        "percentage_to_goal": "{:.2f}".format(percentage_to_goal),
    }
    return render(request, "admin/analytics.html", context)
