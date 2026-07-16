from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User

from .forms import PinSetupForm
from .forms import RegisterForm
from .models import SecurityQuestion, UserSecurity
from .forms import MasterPasswordForm
from .forms import SecurityQuestionForm, PasswordRecoveryForm


@login_required
def account_view(request):
    return render(request, "accounts/account.html", {"user": request.user})


def _get_next_setup_redirect(user_security):
    if not user_security.master_password_hash:
        return redirect("setup_master_password")
    if not user_security.pin_hash:
        return redirect("setup_pin")
    if not user_security.security_question_id or not user_security.security_answer_hash:
        return redirect("setup_security_question")
    return redirect("dashboard")


def register_view(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():

            user = form.save()

            login(request, user)

            return redirect("setup_master_password")

    else:

        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):

    if request.method == "POST":

        form = AuthenticationForm(request, data=request.POST)

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            user_security = UserSecurity.objects.filter(user=user).first()

            if user_security and user_security.security_setup_completed:
                return redirect("verify_security_question")

            if user_security:
                return _get_next_setup_redirect(user_security)

            return redirect("setup_master_password")

    else:

        form = AuthenticationForm()

    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):

    logout(request)

    return redirect("login")


def password_recovery_view(request):
    if request.method == "POST":
        form = PasswordRecoveryForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            user = User.objects.filter(email=email).first()
            if user:
                send_mail(
                    "Password recovery requested",
                    f"Hello {user.username}, a password recovery request was received for your account.",
                    "noreply@example.com",
                    [user.email],
                    fail_silently=False,
                )
                return render(
                    request,
                    "accounts/password_recovery.html",
                    {
                        "form": form,
                        "message": f"If an account exists for {email}, we will guide you through recovery.",
                    },
                )
            return render(
                request,
                "accounts/password_recovery.html",
                {
                    "form": form,
                    "message": "If an account exists for this email, a recovery guide will be sent.",
                },
            )
    else:
        form = PasswordRecoveryForm()

    return render(request, "accounts/password_recovery.html", {"form": form, "message": "Enter your email to recover your account."})


@login_required
def setup_master_password(request):

    security, created = UserSecurity.objects.get_or_create(
        user=request.user
    )

    if security.security_setup_completed:
        return redirect("dashboard")

    if security.master_password_hash:
        return _get_next_setup_redirect(security)

    if request.method == "POST":

        form = MasterPasswordForm(request.POST)

        if form.is_valid():

            security.master_password_hash = make_password(
                form.cleaned_data["master_password"]
            )

            security.password_hint = form.cleaned_data["password_hint"]

            security.save()

            return redirect("setup_pin")

    else:

        form = MasterPasswordForm()

    return render(
        request,
        "accounts/setup_master_password.html",
        {
            "form": form
        }
    )


@login_required
def setup_pin(request):

    security = UserSecurity.objects.get(user=request.user)

    if security.security_setup_completed:
        return redirect("dashboard")

    if not security.master_password_hash:
        return redirect("setup_master_password")

    if security.pin_hash:
        return _get_next_setup_redirect(security)

    if request.method == "POST":

        form = PinSetupForm(request.POST)

        if form.is_valid():

            security.pin_hash = make_password(
                form.cleaned_data["pin"]
            )

            security.save()

            return redirect("setup_security_question")

    else:

        form = PinSetupForm()

    return render(
        request,
        "accounts/setup_pin.html",
        {
            "form": form
        }
    )


@login_required
def setup_security_question(request):

    security = UserSecurity.objects.get(user=request.user)

    if security.security_setup_completed:
        return redirect("dashboard")

    if not security.master_password_hash:
        return redirect("setup_master_password")

    if not security.pin_hash:
        return redirect("setup_pin")

    if request.method == "POST":

        form = SecurityQuestionForm(request.POST)

        if form.is_valid():
            if not security.security_question:
                question_text = "What is your favorite color?"
                security_question, _ = SecurityQuestion.objects.get_or_create(question=question_text)
                security.security_question = security_question

            security.security_answer_hash = make_password(
                form.cleaned_data["answer"]
            )
            security.security_setup_completed = True

            security.save()

            return redirect("dashboard")

    else:

        form = SecurityQuestionForm()

    return render(
        request,
        "accounts/setup_security_question.html",
        {
            "form": form,
            "question": security.security_question.question if security.security_question else "What is your favorite color?"
        }
    )


@login_required
def verify_security_question(request):
    security = UserSecurity.objects.get(user=request.user)

    if not security.security_setup_completed:
        return redirect("dashboard")

    if request.method == "POST":
        form = SecurityQuestionForm(request.POST)
        if form.is_valid():
            from django.contrib.auth.hashers import check_password

            if check_password(form.cleaned_data["answer"], security.security_answer_hash):
                return redirect("dashboard")
            form.add_error("answer", "Incorrect answer. Please try again.")
    else:
        form = SecurityQuestionForm()

    return render(
        request,
        "accounts/verify_security_question.html",
        {
            "form": form,
            "question": security.security_question.question if security.security_question else "What is your favorite color?"
        },
    )