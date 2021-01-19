from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
import stripe
from decouple import config

from ..forms import RegisterForm, LoginForm
from ..models import Therapist


def signup_user(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            email = form.cleaned_data.get("email")
            if User.objects.filter(username=email).count() == 0:
                user.username = email
                user.email = email
                user.save()
                name = form.cleaned_data.get("first_name")
                account = Therapist(name=name, user=user)
                account.save()
                raw_password = form.cleaned_data.get("password1")
                user = authenticate(username=user.username, password=raw_password)
                if user:
                    stripe.api_key = config("STRIPE_SECRET")
                    stripe_customer = stripe.Customer.create(email=email)
                    account.stripe_customer_id = stripe_customer["id"]
                    account.save()
                    login(request, user)
                    return redirect(reverse("home"))
    else:
        form = RegisterForm()
    return render(request, "theralogs/auth/signup.html", {"form": form})


def login_user(request):
    form = LoginForm(request.POST or None)
    if request.POST and form.is_valid():
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")
        user = authenticate(username=email, password=password)
        if user:
            login(request, user)
            return redirect(reverse("home"))
    return render(request, "theralogs/auth/login.html", {"form": form})


@login_required
def logout_user(request):
    logout(request)
    return redirect(reverse("login"))
