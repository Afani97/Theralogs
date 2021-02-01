from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from django.urls import path
from .views import main, auth, profile, patient, rn

urlpatterns = [
    path("", main.LandingPage.as_view(), name="landing-page"),
    path("main/", main.main_view, name="home"),
    path("main/file-upload/", main.file_upload, name="file_upload"),
    path(
        "main/resend-email/<uuid:session_id>/", main.resend_email, name="resend-email"
    ),
    path("main/aai-webhook", main.transcribe_webhook, name="aai-webhook"),
    path("main/<str:filter_date>/", main.main_view, name="filter_main"),
    path("signup/", auth.signup_user, name="signup"),
    path("login/", auth.login_user, name="login"),
    path("logout/", auth.logout_user, name="logout"),
    path("patient/create/", patient.create_patient, name="patient_create"),
    path("patient/<uuid:patient_id>/edit/", patient.edit_patient, name="patient_edit"),
    path(
        "patient/<uuid:patient_id>/delete/",
        patient.delete_patient,
        name="patient_delete",
    ),
    path("profile/", profile.view_profile, name="profile"),
    path("profile/edit/", profile.EditProfileView.as_view(), name="edit_profile"),
    path("profile/update_payment/", profile.update_payment, name="update_payment"),
    path("rn/main/", rn.MainView.as_view()),
    path("rn/profile/", rn.ProfileView.as_view()),
    path("rn/file-upload/", rn.AudioUploadView.as_view()),
    path("rn/patient/create/", rn.CreatePatientView.as_view()),
]

# JWT
urlpatterns += [
    path("rn/auth/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("rn/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
