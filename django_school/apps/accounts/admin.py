from django.contrib import admin

from django_school.apps.accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
