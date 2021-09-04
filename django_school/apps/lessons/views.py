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
from django_school.apps.lessons.models import Lesson, LessonSession

User = get_user_model()

SUCCESS_LESSON_SESSION_UPDATE_MESSAGE = (
    "The lesson session has been saved successfully."
)


class TimetableContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lessons_times"] = Lesson.LESSONS_TIMES
        context["weekdays"] = Lesson.WEEKDAYS

        return context


class ClassTimetableView(TimetableContextMixin, DetailView):
    model = Class
    context_object_name = "school_class"
    template_name = "lessons/class_timetable.html"

    def get_queryset(self):
        return super().get_queryset().with_lessons()


class TeacherTimetableView(TimetableContextMixin, DetailView):
    model = User
    context_object_name = "teacher"
    template_name = "lessons/teacher_timetable.html"

    def get_object(self, queryset=None):
        user = super().get_object()

        if not user.is_teacher:
            raise Http404

        return user

    def get_queryset(self):
        return self.model.objects.with_nested_teacher_resources()


def timetables_list_view(request):
    teachers = User.objects.filter(groups__name="teachers").order_by("first_name")
    school_classes = Class.objects.order_by("number")

    return render(
        request,
        "lessons/timetable_list.html",
        {"teachers": teachers, "school_classes": school_classes},
    )


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
            .with_nested_resources()
            .filter(lesson__teacher=self.request.user, date=date)
        )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["date"] = self.request.GET.get("date")

        return context


@login_required
@permission_required("lessons.change_lessonsession", raise_exception=True)
def lesson_session_detail_view(request, pk):
    lesson_session = get_object_or_404(
        LessonSession.objects.with_nested_resources(),
        pk=pk,
    )

    if request.user != lesson_session.lesson.teacher:
        raise PermissionDenied()

    if request.method == "POST":
        lesson_session_form = LessonSessionForm(request.POST, instance=lesson_session)
        presences_formset = PresenceFormSet(request.POST, instance=lesson_session)
        if lesson_session_form.is_valid() and presences_formset.is_valid():
            lesson_session_form.save()
            presences_formset.save()
            messages.success(request, SUCCESS_LESSON_SESSION_UPDATE_MESSAGE)
            return redirect("lessons:sessions")
    else:
        lesson_session_form = LessonSessionForm(instance=lesson_session)
        presences_formset = PresenceFormSet(instance=lesson_session)

    return render(
        request,
        "lessons/lesson_session_detail.html",
        {
            "lesson_session_form": lesson_session_form,
            "lesson_session": lesson_session,
            "presences_formset": presences_formset,
        },
    )
