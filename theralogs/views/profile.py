from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView

from theralogs.forms import EditProfileForm, UpdatePaymentForm
from theralogs.managers.stripe_manager import stripe_manager
from theralogs.models import Therapist


@login_required
def view_profile(request):
    context = {
        "profile": request.user.therapist,
        "patients": request.user.therapist.patient_set.all(),
    }
    return render(request, "theralogs/profile/profile.html", context)


@method_decorator(login_required, name="dispatch")
class EditProfileView(UpdateView):
    model = Therapist
    form_class = EditProfileForm
    template_name = "theralogs/profile/edit_profile.html"
    success_url = reverse_lazy("profile")

    def get_initial(self):
        return {"email": self.request.user.email}

    def get_object(self):
        return self.request.user.therapist

    def get_form(self):
        form = super(EditProfileView, self).get_form(EditProfileForm)
        form.user = self.request.user
        return form

    def form_valid(self, form):
        form.save()
        return redirect(reverse_lazy("profile"))


@login_required
def update_payment(request):
    payment_form = UpdatePaymentForm()
    if request.method == "POST":
        payment_form = UpdatePaymentForm(request.POST)
        if payment_form.is_valid():
            card_dict = {
                "number": payment_form.cleaned_data.get("card_number"),
                "exp_month": payment_form.cleaned_data.get("card_exp_month"),
                "exp_year": payment_form.cleaned_data.get("card_exp_year"),
                "cvc": payment_form.cleaned_data.get("card_cvc"),
            }
            stripe_saved = stripe_manager.create_payment_method(
                therapist=request.user.therapist, card_dict=card_dict
            )
            if stripe_saved:
                return redirect("profile")
            response = render(
                request, "theralogs/profile/update_payment.html", {"form": payment_form}
            )
            response.status_code = 400
            return response
        else:
            response = render(
                request, "theralogs/profile/update_payment.html", {"form": payment_form}
            )
            response.status_code = 400
            return response
    return render(
        request, "theralogs/profile/update_payment.html", {"form": payment_form}
    )
