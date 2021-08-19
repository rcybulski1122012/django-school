from django.contrib import admin

from django_school.apps.grades.models import Grade


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    pass
