import datetime

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from django_school.apps.classes.models import Class
from django_school.apps.common.utils import (RolesRequiredMixin,
                                             SubjectAndSchoolClassRelatedMixin,
                                             ajax_required, roles_required)
from django_school.apps.lessons.forms import (AttendanceFormSet, HomeworkForm,
                                              HomeworkRealisationForm,
                                              LessonSessionForm)
from django_school.apps.lessons.models import (Homework, Lesson, LessonSession,
                                               Subject)
from django_school.apps.users.models import ROLES

User = get_user_model()


class TimetableContextMixin:
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lessons_times"] = Lesson.LESSONS_TIMES
        context["weekdays"] = Lesson.WEEKDAYS

        return context


class ClassTimetableView(TimetableContextMixin, DetailView):
    model = Class
    slug_url_kwarg = "class_slug"
    template_name = "lessons/class_timetable.html"
    context_object_name = "school_class"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("lessons__subject", "lessons__teacher")
        )


class TeacherTimetableView(TimetableContextMixin, DetailView):
    model = User
    slug_url_kwarg = "teacher_slug"
    template_name = "lessons/teacher_timetable.html"
    context_object_name = "teacher"

    def get_queryset(self):
        return self.model.objects.select_related("address", "teacher_class")

    def get_object(self, queryset=None):
        user = super().get_object()

        if not user.is_teacher:
            raise Http404

        return user


def timetable_list_view(request):
    teachers = User.teachers.order_by("first_name")
    school_classes = Class.objects.order_by("number")

    return render(
        request,
        "lessons/timetable_list.html",
        {"teachers": teachers, "school_classes": school_classes},
    )


class LessonSessionListView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER, ROLES.STUDENT), ListView
):
    model = LessonSession
    template_name = "lessons/teacher_lesson_session_list.html"
    context_object_name = "lesson_sessions"

    def get_queryset(self):
        date = self.request.GET.get("date", datetime.date.today())

        qs = (
            super()
            .get_queryset()
            .visible_to_user(self.request.user)
            .filter(date=date)
            .select_related(
                "lesson__teacher",
                "lesson__school_class",
                "lesson__subject",
            )
        )

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["date"] = self.request.GET.get("date")

        return context


@login_required
@roles_required(ROLES.TEACHER, ROLES.STUDENT)
def lesson_session_detail_view(request, session_pk):
    lesson_session = get_object_or_404(
        LessonSession.objects.with_related_objects()
        .visible_to_user(request.user)
        .prefetch_related("attached_files"),
        pk=session_pk,
    )

    lesson_session_form = LessonSessionForm(
        request.POST or None,
        request.FILES or None,
        instance=lesson_session,
        disabled=not request.user.is_teacher,
        teacher=request.user,
    )
    attendance_formset = AttendanceFormSet(
        request.POST or None, instance=lesson_session
    )

    if request.method == "POST" and request.user.is_teacher:
        if lesson_session_form.is_valid() and attendance_formset.is_valid():
            lesson_session_form.save()
            attendance_formset.save()
            messages.success(
                request, "The lesson session has been updated successfully."
            )
            return redirect(lesson_session.detail_url)

    ctx = {
        "lesson_session_form": lesson_session_form,
        "lesson_session": lesson_session,
        "attendance_formset": attendance_formset,
    }

    if request.user.is_student:
        ctx["attendance_status"] = lesson_session.attendance_set.get(
            student=request.user
        ).status

    return render(
        request,
        "lessons/lesson_session_detail.html",
        ctx,
    )


class ClassSubjectListView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER), ListView
):
    model = Subject
    template_name = "lessons/class_subject_list.html"
    context_object_name = "subjects"

    school_class = None

    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(Class, slug=self.kwargs["class_slug"])
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_does_the_teacher_teach_the_subject_to_the_class(
                teacher=self.request.user, school_class=self.school_class
            )
            .filter(lessons__school_class=self.school_class)
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["school_class"] = self.school_class

        return context


@login_required
def student_attendance_summary_view(request, student_slug):
    subject_name = request.GET.get("subject", None)
    subject = (
        get_object_or_404(Subject, name__iexact=subject_name) if subject_name else None
    )
    if subject:
        attendance_params = {"attendance__lesson_session__lesson__subject": subject}
    else:
        attendance_params = {}

    student = get_object_or_404(
        User.students.visible_to_user(request.user).with_attendance(
            **attendance_params
        ),
        slug=student_slug,
    )
    subjects = Subject.objects.filter(
        lessons__school_class__students=student
    ).values_list("name", flat=True)

    ctx = {
        "student": student,
        "subject": subject,
        "subjects": subjects,
    }

    return render(request, "lessons/student_attendance.html", ctx)


@login_required
@roles_required(ROLES.TEACHER)
def class_attendance_summary_view(request, class_slug):
    school_class = get_object_or_404(
        Class.objects.visible_to_user(request.user), slug=class_slug
    )

    students = User.students.filter(school_class=school_class).with_attendance()

    ctx = {
        "students": students,
        "school_class": school_class,
    }

    return render(request, "lessons/class_attendance.html", ctx)


class SetHomeworkView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SuccessMessageMixin,
    SubjectAndSchoolClassRelatedMixin,
    CreateView,
):
    model = Homework
    form_class = HomeworkForm
    success_url = reverse_lazy("lessons:homework_list")
    success_message = "The homework has been set successfully"
    template_name = "lessons/homework_set.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update(
            {
                "teacher": self.request.user,
                "school_class": self.school_class,
                "subject": self.subject,
            }
        )

        return kwargs


class HomeworkListView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER, ROLES.STUDENT), ListView
):
    model = Homework
    paginate_by = 10
    template_name = "lessons/homework_list.html"
    context_object_name = "homeworks"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .visible_to_user(self.request.user)
            .only_current()
            .select_related("subject", "school_class")
            .order_by("completion_date")
        )

        if self.request.user.is_teacher:
            return qs.with_realisations_count()
        else:
            return qs.with_realisations(self.request.user)


class HomeworkDetailView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER, ROLES.STUDENT),
    DetailView,
):
    model = Homework
    pk_url_kwarg = "homework_pk"
    template_name = "lessons/homework_detail.html"
    context_object_name = "homework"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .visible_to_user(self.request.user)
            .select_related("subject", "school_class")
            .prefetch_related("attached_files")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_student:
            realisation = (
                self.object.realisations.filter(student=self.request.user)
                .prefetch_related("attached_files")
                .first()
            )
            ctx["homework_realisation"] = realisation
        else:
            students = User.students.with_homework_realisations(self.object)
            ctx["students"] = students

        return ctx


@login_required
@roles_required(ROLES.STUDENT)
@ajax_required
def submit_homework_realisation_view(request, homework_pk):
    homework = get_object_or_404(
        Homework.objects.visible_to_user(request.user), pk=homework_pk
    )

    if homework.realisations.filter(student=request.user).exists():
        raise PermissionDenied()

    form = HomeworkRealisationForm(
        data=request.POST or None,
        files=request.FILES or None,
        student=request.user,
        homework=homework,
    )

    if request.method == "POST":
        if form.is_valid():
            form.save()
            messages.success(
                request, "Your realisation has been submitted successfully"
            )
            return redirect(homework.detail_url)

    ctx = {"form": form}
    return render(request, "lessons/modals/homework_realisation_create.html", ctx)
