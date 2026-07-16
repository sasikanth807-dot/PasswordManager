from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class SecurityQuestionForm(forms.Form):
    answer = forms.CharField(widget=forms.PasswordInput())


class PasswordRecoveryForm(forms.Form):
    email = forms.EmailField(required=True)


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password1",
            "password2",
        ]


class MasterPasswordForm(forms.Form):

    master_password = forms.CharField(
        widget=forms.PasswordInput()
    )

    confirm_master_password = forms.CharField(
        widget=forms.PasswordInput()
    )

    password_hint = forms.CharField(
        max_length=255
    )

    def clean(self):
        cleaned_data = super().clean()

        mp = cleaned_data.get("master_password")
        cmp = cleaned_data.get("confirm_master_password")

        if mp != cmp:
            raise forms.ValidationError(
                "Master passwords do not match."
            )

        return cleaned_data


class PinSetupForm(forms.Form):

    pin = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=6,
        min_length=6
    )

    confirm_pin = forms.CharField(
        widget=forms.PasswordInput(),
        max_length=6,
        min_length=6
    )

    def clean(self):
        cleaned_data = super().clean()

        pin = cleaned_data.get("pin")
        confirm = cleaned_data.get("confirm_pin")

        if pin != confirm:
            raise forms.ValidationError(
                "PIN does not match."
            )

        if pin and not pin.isdigit():
            raise forms.ValidationError(
                "PIN must contain only digits."
            )

        return cleaned_data