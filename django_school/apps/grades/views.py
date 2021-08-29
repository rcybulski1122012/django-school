from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView

from django_school.apps.classes.models import Class
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import Lesson, Subject

User = get_user_model()

SUCCESS_GRADE_CREATE_MESSAGE = "Grade was added successfully."


class GradeCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Grade
    fields = ("grade", "category", "weight", "comment", "subject", "student", "teacher")
    permission_required = "grades.add_grade"
    success_message = SUCCESS_GRADE_CREATE_MESSAGE
    slug_url_kwarg = "class_slug"

    def get_initial(self):
        return {
            "subject": self.request.GET.get("subject"),
            "student": self.request.GET.get("student"),
        }

    def get_form(self, **kwargs):
        # TODO: this view should also accept subject_slug as an url parameter
        form = super().get_form(**kwargs)
        form.fields["teacher"].widget = forms.HiddenInput()
        form.fields["teacher"].initial = self.request.user.pk

        school_class = get_object_or_404(Class, slug=self.kwargs["class_slug"])
        # subject = get_object_or_404(Subject, slug=self.kwargs["subject_slug"])

        subjects_qs = Subject.objects.filter(
            lessons__teacher=self.request.user, lessons__school_class=school_class
        ).distinct()
        students_qs = User.objects.filter(school_class=school_class)

        grades_categories_qs = GradeCategory.objects.filter(
            subject__in=subjects_qs, school_class=school_class
        )

        if not subjects_qs.exists():
            raise PermissionDenied

        form.fields["subject"].queryset = subjects_qs
        form.fields["student"].queryset = students_qs
        form.fields["category"].queryset = grades_categories_qs

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.kwargs["class_slug"]

        return context

    def form_valid(self, form):
        self.form = form
        return super().form_valid(form)

    def get_success_url(self):
        instance = self.form.instance
        return reverse(
            "grades:class_grades",
            args=[instance.student.school_class.slug, instance.subject.slug],
        )


@login_required
@permission_required("grades.add_grade", raise_exception=True)
def class_grades_view(request, class_slug, subject_slug):
    school_class = get_object_or_404(Class, slug=class_slug)
    subject = get_object_or_404(Subject, slug=subject_slug)

    if not Lesson.objects.filter(
        subject=subject, school_class=school_class, teacher=request.user
    ).exists():
        raise Http404

    categories = GradeCategory.objects.filter(
        subject=subject, school_class=school_class
    )
    students = User.objects.with_nested_student_resources().filter(
        school_class=school_class
    )

    return render(
        request,
        "grades/class_grades.html",
        {
            "categories": categories,
            "students": students,
            "school_class": school_class,
            "subject": subject,
        },
    )
