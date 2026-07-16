from django.db import models
from django.contrib.auth.models import User


class SecurityQuestion(models.Model):
    question = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.question


class UserSecurity(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    master_password_hash = models.CharField(max_length=255, blank=True, default="")
    password_hint = models.CharField(max_length=255, blank=True, default="")
    pin_hash = models.CharField(max_length=255, blank=True, default="")

    security_question = models.ForeignKey(
        SecurityQuestion,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    security_answer_hash = models.CharField(max_length=255, blank=True, default="")
    recovery_key_hash = models.CharField(max_length=255, blank=True, default="")

    security_setup_completed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username