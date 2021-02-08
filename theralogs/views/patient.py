from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render

from theralogs.forms import EditPatientForm, NewPatientForm
from theralogs.models import Patient


@login_required
def create_patient(request):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        patient_name = request.POST.get("patient-name")
        patient_email = request.POST.get("patient-email")
        if patient_name and patient_email:
            patient = Patient(
                name=patient_name, email=patient_email, therapist=request.user.therapist
            )
            patient.save()
            context = {"msg": "success", "patient_id": patient.id}
            return JsonResponse(context, status=200)
        else:
            return JsonResponse({"msg": "error"}, status=400)
    else:
        form = NewPatientForm()
        if request.method == "POST":
            form = NewPatientForm(request.POST)
            if form.is_valid():
                patient = Patient(
                    name=form.cleaned_data.get("name"),
                    email=form.cleaned_data.get("email"),
                    therapist=request.user.therapist,
                )
                patient.save()
                return redirect("profile")
            else:
                response = render(
                    request, "theralogs/patient/new_patient.html", {"form": form}
                )
                response.status_code = 400
                return response
        return render(request, "theralogs/patient/new_patient.html", {"form": form})
    return redirect("profile")


@login_required
def edit_patient(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    form = EditPatientForm(instance=patient)
    if request.method == "POST":
        form = EditPatientForm(request.POST)
        if form.is_valid():
            patient.name = form.cleaned_data.get("name")
            patient.email = form.cleaned_data.get("email")
            patient.save()
            return redirect("profile")
        else:
            response = render(
                request, "theralogs/patient/edit_patient.html", {"form": form}
            )
            response.status_code = 400
            return response
    return render(request, "theralogs/patient/edit_patient.html", {"form": form})


@login_required
def delete_patient(request, patient_id):
    patient = Patient.objects.filter(id=patient_id).first()
    if patient:
        if request.method == "POST":
            patient.delete()
            return redirect("profile")
        context = {"patient_name": patient.name}
        return render(request, "theralogs/patient/delete_patient.html", context)
    return HttpResponse("Patient not found", status=400)
