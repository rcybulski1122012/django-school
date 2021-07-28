from django.contrib import admin

from django_school.apps.users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass
