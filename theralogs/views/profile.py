import stripe
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import UpdateView
from decouple import config

from theralogs.forms import EditProfileForm, UpdatePaymentForm
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
            stripe.api_key = config("STRIPE_SECRET")
            stripe_payment_method = stripe.PaymentMethod.create(
                type="card",
                card={
                    "number": payment_form.cleaned_data.get("card_number"),
                    "exp_month": payment_form.cleaned_data.get("card_exp_month"),
                    "exp_year": payment_form.cleaned_data.get("card_exp_year"),
                    "cvc": payment_form.cleaned_data.get("card_cvc"),
                },
            )
            therapist = request.user.therapist
            if therapist.stripe_payment_method_id:
                stripe.PaymentMethod.detach(
                    therapist.stripe_payment_method_id,
                )

            therapist.stripe_payment_method_id = stripe_payment_method["id"]
            stripe.PaymentMethod.attach(
                therapist.stripe_payment_method_id,
                customer=therapist.stripe_customer_id,
            )
            therapist.save()
            return redirect("profile")
    context = {"form": payment_form}
    return render(request, "theralogs/profile/update_payment.html", context)
