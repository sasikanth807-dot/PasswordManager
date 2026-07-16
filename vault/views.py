from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from .models import VaultEntry


class VaultEntryForm(forms.ModelForm):
    website = forms.CharField(required=False, max_length=200)

    def clean_website(self):
        website = self.cleaned_data.get("website", "")
        if website:
            website = website.strip()
            if not website.startswith(("http://", "https://")):
                website = website
        return website

    class Meta:
        model = VaultEntry
        fields = ["title", "username", "password", "website", "notes"]


@login_required
def vault_view(request):
    entries = VaultEntry.objects.filter(user=request.user).order_by("-created_at")

    if request.method == "POST":
        form = VaultEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()
            messages.success(request, "Entry saved successfully.")
            return redirect("vault")
        return render(request, "vault/index.html", {"items": entries, "form": form})

    form = VaultEntryForm()
    return render(request, "vault/index.html", {"items": entries, "form": form})
