from django.contrib import admin

from django_school.apps.lessons.models import (AttachedFile, Lesson,
                                               LessonSession, Presence,
                                               Subject)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass


@admin.register(LessonSession)
class LessonSessionAdmin(admin.ModelAdmin):
    pass


@admin.register(Presence)
class PresenceAdmin(admin.ModelAdmin):
    pass


@admin.register(AttachedFile)
class AttachedFileAdmin(admin.ModelAdmin):
    pass
