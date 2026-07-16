from django.db import models
from django.contrib.auth.models import User


class VaultEntry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="vault_entries")
    title = models.CharField(max_length=200)
    username = models.CharField(max_length=200, blank=True)
    password = models.CharField(max_length=500)
    website = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
