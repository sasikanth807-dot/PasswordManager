from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

from .models import VaultEntry


class VaultEntryTests(TestCase):
    def test_vault_entry_accepts_simple_website_name(self):
        user = User.objects.create_user(username="siteuser", password="secret123")
        self.client.force_login(user)

        response = self.client.post(
            reverse("vault"),
            {
                "title": "Example",
                "username": "alice",
                "password": "secret",
                "website": "example.com",
                "notes": "demo",
            },
        )

        self.assertEqual(response.status_code, 302)
        entry = VaultEntry.objects.get(user=user, title="Example")
        self.assertEqual(entry.website, "example.com")

    def test_vault_entry_is_saved_and_displayed_for_logged_in_user(self):
        user = User.objects.create_user(username="vaultuser", password="secret123")
        self.client.force_login(user)

        response = self.client.post(
            reverse("vault"),
            {
                "title": "GitHub",
                "username": "alice",
                "password": "secret",
                "website": "https://example.com",
                "notes": "demo note",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(VaultEntry.objects.filter(user=user).exists())

        follow_response = self.client.get(reverse("vault"))
        self.assertContains(follow_response, "GitHub")
        self.assertContains(follow_response, "saved successfully")
