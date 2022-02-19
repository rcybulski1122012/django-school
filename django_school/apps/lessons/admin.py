from django.contrib import admin

from django_school.apps.lessons.models import (Attendance, Lesson,
                                               LessonSession, Subject)


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    pass


@admin.register(LessonSession)
class LessonSessionAdmin(admin.ModelAdmin):
    list_filter = (
        "lesson__school_class",
        "date",
        "lesson__subject",
    )
    list_select_related = (
        "lesson__school_class",
        "lesson__subject",
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    pass
