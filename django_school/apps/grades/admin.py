from django.contrib import admin

from django_school.apps.grades.models import Grade, GradeCategory


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    pass


@admin.register(GradeCategory)
class GradeCategoryAdmin(admin.ModelAdmin):
    pass
