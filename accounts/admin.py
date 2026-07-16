from django.contrib import admin
from .models import SecurityQuestion, UserSecurity

admin.site.register(UserSecurity)
admin.site.register(SecurityQuestion)