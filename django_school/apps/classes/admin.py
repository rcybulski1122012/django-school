from django.contrib import admin

from django_school.apps.classes.models import Class


@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ("number", "tutor")
    prepopulated_fields = {"slug": ("number",)}
