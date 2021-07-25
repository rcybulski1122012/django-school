from django.contrib import admin

from django_school.apps.classes.models import Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    pass
