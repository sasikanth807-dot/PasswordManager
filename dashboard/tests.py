from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from vault.models import VaultEntry


class DashboardViewTests(TestCase):
    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_renders_for_authenticated_user(self):
        user = User.objects.create_user(username="carol", password="secret123")
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Welcome")
        self.assertContains(response, user.username)

    def test_dashboard_shows_saved_accounts_count(self):
        user = User.objects.create_user(username="dave", password="secret123")
        self.client.force_login(user)

        VaultEntry.objects.create(user=user, title="GitHub", username="dave", password="secret")
        VaultEntry.objects.create(user=user, title="Email", username="dave", password="secret")

        response = self.client.get(reverse("dashboard"))

        self.assertContains(response, "Saved accounts")
        self.assertContains(response, "2")
