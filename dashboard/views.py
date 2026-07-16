from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from vault.models import VaultEntry


@login_required
def dashboard_view(request):
    saved_accounts = VaultEntry.objects.filter(user=request.user).count()
    return render(
        request,
        "dashboard/index.html",
        {"user": request.user, "saved_accounts": saved_accounts},
    )
