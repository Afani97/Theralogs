from datetime import datetime

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from theralogs.models import Therapist, Patient


class RegisterForm(UserCreationForm, forms.ModelForm):
    email = forms.EmailField(label="Email")
    first_name = forms.CharField(label="First name")

    class Meta:
        model = User
        fields = (
            "first_name",
            "email",
            "password1",
        )


class LoginForm(forms.ModelForm):
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(
        label="Password", widget=forms.PasswordInput, required=True
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
    # profile_image = forms.ImageField(label='Profile image', required=False)
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "example@test.com"}),
    )

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email != self.user.email and User.objects.filter(email=email).count() != 0:
            raise ValidationError("Email already taken")
        return email

    # def clean_profile_image(self):
    #     profile_image = self.cleaned_data.get('profile_image')
    #     if profile_image:
    #         file_type = profile_image.image.format
    #         i = Image.open(profile_image)
    #         i.thumbnail((100, 100))
    #         output = io.BytesIO()
    #         i.save(output, format=file_type)
    #         return output.getvalue()
    #     return self.user.cook.profile_image

    class Meta:
        model = Therapist
        fields = ("name", "email", "license_id", "city", "state")
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


class NewPatientForm(forms.ModelForm):
    name = forms.CharField(
        label="First name",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Tom"}),
    )
    email = forms.EmailField(
        label="Email",
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "tom@gmail.com"}),
    )

    class Meta:
        model = Patient
        fields = ("name", "email")
        exclude = ("therapist",)


class EditPatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ("name", "email")
        exclude = ("therapist",)
