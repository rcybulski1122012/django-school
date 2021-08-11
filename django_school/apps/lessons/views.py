from django.contrib.auth import get_user_model
from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, ListView

from django_school.apps.classes.models import Class
from django_school.apps.lessons.models import LESSONS_TIMES, WEEKDAYS

User = get_user_model()


def timetable_list_view(request):
    teachers = User.objects.filter(groups__name="teachers").order_by("first_name")
    school_classes = Class.objects.order_by("number")

    return render(
        request,
        "lessons/timetable_list.html",
        {"teachers": teachers, "school_classes": school_classes},
    )


class TimetableContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lessons_times"] = LESSONS_TIMES
        context["weekdays"] = WEEKDAYS

        return context


class ClassTimetableView(TimetableContextMixin, DetailView):
    model = Class
    context_object_name = "school_class"
    template_name = "lessons/class_timetable.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("lessons__subject", "lessons__teacher")
        )


class TeacherTimetableView(TimetableContextMixin, DetailView):
    model = User
    context_object_name = "teacher"
    template_name = "lessons/teacher_timetable.html"

    def get_object(self, queryset=None):
        user = super().get_object()

        if not user.groups.filter(name="teachers").exists():
            raise Http404

        return user
