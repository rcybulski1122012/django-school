from django.contrib import admin

from django_school.apps.lessons.models import (ExactLesson, Lesson, Presence,
                                               Subject)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    pass


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass


@admin.register(ExactLesson)
class ExactLessonAdmin(admin.ModelAdmin):
    pass


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    pass
