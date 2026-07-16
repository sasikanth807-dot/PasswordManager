from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def security_view(request):
    return render(request, "security/index.html", {"user": request.user})
