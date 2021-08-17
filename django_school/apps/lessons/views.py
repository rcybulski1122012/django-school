import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import DetailView, ListView

from django_school.apps.classes.models import Class
from django_school.apps.lessons.forms import LessonSessionForm, PresenceFormSet
from django_school.apps.lessons.models import LESSONS_TIMES, WEEKDAYS, LessonSession

User = get_user_model()

SUCCESS_LESSON_SESSION_UPDATE_MESSAGE = (
    "The lesson session has been saved successfully."
)


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


class TeacherLessonSessionListView(PermissionRequiredMixin, ListView):
    model = LessonSession
    permission_required = "lessons.view_lessonsession"
    template_name = "lessons/teacher_lesson_sessions_list.html"
    context_object_name = "lesson_sessions"

    def get_queryset(self):
        date = self.request.GET.get("date", datetime.date.today())

        qs = (
            super()
            .get_queryset()
            .select_related("lesson__subject", "lesson__school_class")
            .filter(lesson__teacher=self.request.user)
            .filter(date=date)
        )

        return qs


@login_required
@permission_required("lessons.change_lessonsession", raise_exception=True)
def lesson_session_detail_view(request, pk):
    lesson_session = get_object_or_404(LessonSession, pk=pk)

    if request.user != lesson_session.lesson.teacher:
        raise PermissionDenied()

    if request.method == "POST":
        form = LessonSessionForm(request.POST, instance=lesson_session)
        formset = PresenceFormSet(request.POST, instance=lesson_session)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, SUCCESS_LESSON_SESSION_UPDATE_MESSAGE)
            return redirect("lessons:sessions")
    else:
        form = LessonSessionForm(instance=lesson_session)
        formset = PresenceFormSet(instance=lesson_session)

    return render(
        request,
        "lessons/lesson_session_detail.html",
        {"form": form, "lesson_session": lesson_session, "formset": formset},
    )
