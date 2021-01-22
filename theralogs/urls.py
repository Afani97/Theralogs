from django.urls import path
from .views import main, auth, profile, patient

urlpatterns = [
    path("", main.main_view, name="home"),
    path("file-upload/", main.file_upload, name="file_upload"),
    path("main/<str:filter_date>/", main.main_view, name="filter_main"),
    path("sns/", main.sns_transcribe_event, name="sns"),
    path("resend-email/<uuid:session_id>/", main.resend_email, name="resend-email"),
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
]
