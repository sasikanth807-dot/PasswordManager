from django.urls import path

from . import views

urlpatterns = [

    path("register/", views.register_view, name="register"),

    path("login/", views.login_view, name="login"),

    path("logout/", views.logout_view, name="logout"),
    path("password-recovery/", views.password_recovery_view, name="password_recovery"),
    path(
    "setup-master-password/",
    views.setup_master_password,
    name="setup_master_password",
),
    path(
    "setup-pin/",
    views.setup_pin,
    name="setup_pin",
),
path(
    "setup-security-question/",
    views.setup_security_question,
    name="setup_security_question",
),
path(
    "verify-security-question/",
    views.verify_security_question,
    name="verify_security_question",
),
]