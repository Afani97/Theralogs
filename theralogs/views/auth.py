from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse

from theralogs.managers.stripe_manager import stripe_manager
from ..forms import RegisterForm, LoginForm
from ..models import Therapist
from ..tasks import background_tasks


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
                raw_password = form.cleaned_data.get("password1")
                user = authenticate(username=user.username, password=raw_password)
                if user:
                    name = form.cleaned_data.get("first_name")
                    license_id = form.cleaned_data.get("license_id")
                    stripe_customer_id = stripe_manager.register_customer(
                        email=user.email
                    )
                    account = Therapist(
                        name=name,
                        user=user,
                        license_id=license_id,
                        stripe_customer_id=stripe_customer_id,
                    )
                    account.save()
                    login(request, user)
                    _ = background_tasks.send_new_customer(name, email)
                    return redirect(reverse("home"))
        else:
            response = render(request, "theralogs/auth/signup.html", {"form": form})
            response.status_code = 400
            return response
    else:
        form = RegisterForm()
    return render(request, "theralogs/auth/signup.html", {"form": form})


def login_user(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user = authenticate(username=email, password=password)
            if user:
                login(request, user)
                return redirect(reverse("home"))
        else:
            response = render(request, "theralogs/auth/login.html", {"form": form})
            response.status_code = 400
            return response
    else:
        form = LoginForm()
        return render(request, "theralogs/auth/login.html", {"form": form})


@login_required
def logout_user(request):
    logout(request)
    return redirect(reverse("login"))
