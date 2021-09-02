from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, TemplateView

from django_school.apps.classes.models import Class
from django_school.apps.grades.forms import GradeForm
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import Lesson, Subject

User = get_user_model()

SUCCESS_GRADE_CREATE_MESSAGE = "Grade was added successfully."


class GradesViewMixin:
    def dispatch(self, request, *args, **kwargs):
        self.school_class = get_object_or_404(Class, slug=self.kwargs["class_slug"])
        self.subject = get_object_or_404(Subject, slug=self.kwargs["subject_slug"])

        if not self.does_the_teacher_teach_the_subject_to_the_class():
            raise Http404

        return super().dispatch(request, *args, **kwargs)

    def does_the_teacher_teach_the_subject_to_the_class(self):
        return Lesson.objects.filter(
            school_class=self.school_class,
            subject=self.subject,
            teacher=self.request.user,
        ).exists()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "school_class": self.school_class,
                "subject": self.subject,
            }
        )

        return context


class GradeCreateView(
    PermissionRequiredMixin, SuccessMessageMixin, GradesViewMixin, CreateView
):
    model = Grade
    form_class = GradeForm
    permission_required = "grades.add_grade"
    success_message = SUCCESS_GRADE_CREATE_MESSAGE

    def get_initial(self):
        return {
            "student": self.request.GET.get("student"),
            "teacher": self.request.user.pk,
            "subject": self.subject.pk,
        }

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)

        students_qs = User.objects.filter(school_class=self.school_class)
        grades_categories_qs = GradeCategory.objects.filter(
            subject=self.subject, school_class=self.school_class
        )

        form.fields["student"].queryset = students_qs
        form.fields["category"].queryset = grades_categories_qs

        return form

    def get_success_url(self):
        return reverse(
            "grades:class_grades",
            args=[self.kwargs["class_slug"], self.kwargs["subject_slug"]],
        )


class ClassGradesView(PermissionRequiredMixin, GradesViewMixin, TemplateView):
    permission_required = "grades.view_grade"
    template_name = "grades/class_grades.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            {
                "categories": GradeCategory.objects.filter(
                    subject=self.subject, school_class=self.school_class
                ),
                "students": User.objects.with_nested_student_resources().filter(
                    school_class=self.school_class
                ),
            }
        )

        return context
