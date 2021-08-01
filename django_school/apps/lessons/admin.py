from django.contrib import admin

from django_school.apps.lessons.models import Lesson, Subject


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass
