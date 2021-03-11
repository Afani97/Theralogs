from datetime import datetime

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from theralogs.models import Therapist, Patient


class RegisterForm(UserCreationForm, forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "example@test.com"}),
    )
    first_name = forms.CharField(
        label="First name",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Tom"}),
    )
    license_id = forms.CharField(
        label="License ID",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "23524525"}),
    )

    password1 = forms.CharField(
        label="Password",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "*********", "type": "password"}),
    )

    password2 = forms.CharField(
        label="Confirm Password",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "*********", "type": "password"}),
    )

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if not first_name.isalpha():
            raise ValidationError("Only valid names allowed.")
        return first_name

    class Meta:
        model = User
        fields = (
            "first_name",
            "email",
            "license_id",
            "password1",
            "password2",
        )


class LoginForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.EmailInput(attrs={"placeholder": "tom@test.com"}),
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(
            attrs={"placeholder": "*********", "type": "password"}
        ),
        required=True,
    )

    def clean(self):
        user = authenticate(
            username=self.cleaned_data.get("email"),
            password=self.cleaned_data.get("password"),
        )
        if not user:
            raise forms.ValidationError(
                "Sorry, that login was invalid. Please try again."
            )
        return self.cleaned_data

    class Meta:
        model = User
        fields = (
            "email",
            "password",
        )


class EditProfileForm(forms.ModelForm):
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "example@test.com"}),
    )

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name.isalpha():
            raise ValidationError("Only valid names allowed.")
        return name

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email != self.user.email
            and User.objects.filter(username=email).count() != 0
        ):
            raise ValidationError("Email already taken")
        return email

    class Meta:
        model = Therapist
        fields = (
            "name",
            "email",
            "license_id",
        )
        exclude = ("user",)


class UpdatePaymentForm(forms.Form):
    card_number = forms.CharField(
        required=True,
        max_length=16,
        min_length=16,
        widget=forms.TextInput(attrs={"placeholder": "0000 0000 0000 0000"}),
    )
    card_exp_month = forms.IntegerField(
        required=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        widget=forms.TextInput(attrs={"placeholder": "8"}),
    )
    card_exp_year = forms.IntegerField(
        required=True,
        validators=[
            MinValueValidator(datetime.now().year),
            MaxValueValidator(datetime.now().year + 10),
        ],
        widget=forms.TextInput(attrs={"placeholder": "2025"}),
    )
    card_cvc = forms.CharField(
        required=True,
        max_length=3,
        min_length=3,
        widget=forms.TextInput(attrs={"placeholder": "123"}),
    )


class PatientInfoForm(forms.ModelForm):
    name = forms.CharField(
        label="First name",
        required=True,
        min_length=2,
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Tom"}),
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "tom@gmail.com"}),
    )

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if not name.isalpha():
            raise ValidationError("Only valid names allowed.")
        return name

    class Meta:
        model = Patient
        fields = ("name", "email")
        exclude = ("therapist",)


class ContactUsForm(forms.Form):
    name = forms.CharField(
        label="First name",
        required=True,
        min_length=2,
        max_length=100,
        widget=forms.TextInput(attrs={"placeholder": "Tom"}),
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "tom@gmail.com"}),
    )
    question = forms.CharField(
        label="Your question",
        required=True,
        min_length=1,
        widget=forms.Textarea(attrs={"placeholder": "I have a question about..."}),
    )
