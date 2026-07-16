from django.core import mail
from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password

from .models import SecurityQuestion, UserSecurity


class AccountSetupRedirectTests(TestCase):
    def test_setup_master_password_redirects_to_pin_when_already_configured(self):
        user = User.objects.create_user(username="alice", password="secret123")
        UserSecurity.objects.create(user=user, master_password_hash="hashed")

        self.client.force_login(user)
        response = self.client.get(reverse("setup_master_password"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("setup_pin"))

    def test_setup_security_question_marks_setup_complete_and_redirects_to_dashboard(self):
        user = User.objects.create_user(username="bob", password="secret123")
        security = UserSecurity.objects.create(user=user, master_password_hash="hashed", pin_hash="hashed")
        question = SecurityQuestion.objects.create(question="What is your favorite color?")

        self.client.force_login(user)
        response = self.client.post(
            reverse("setup_security_question"),
            {
                "answer": "blue",
            },
        )

        security.refresh_from_db()
        self.assertTrue(security.security_setup_completed)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("dashboard"))

    def test_login_redirects_to_security_question_check_when_setup_is_complete(self):
        user = User.objects.create_user(username="carol", password="secret123")
        security = UserSecurity.objects.create(
            user=user,
            master_password_hash="hashed",
            pin_hash="hashed",
            security_setup_completed=True,
        )
        question = SecurityQuestion.objects.create(question="What is your favorite color?")
        security.security_question = question
        security.security_answer_hash = make_password("blue")
        security.save()

        response = self.client.post(
            reverse("login"),
            {"username": "carol", "password": "secret123"},
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("verify_security_question"))


class PasswordRecoveryTests(TestCase):
    def test_password_recovery_shows_message_for_existing_email(self):
        user = User.objects.create_user(
            username="recoveryuser",
            email="recovery@example.com",
            password="secret123",
        )

        response = self.client.post(reverse("password_recovery"), {"email": user.email})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Recover Your Account")
        self.assertContains(response, "recovery@example.com")

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_password_recovery_sends_email_for_existing_account(self):
        user = User.objects.create_user(
            username="mailuser",
            email="mail@example.com",
            password="secret123",
        )

        response = self.client.post(reverse("password_recovery"), {"email": user.email})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Password recovery requested", mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to, [user.email])
