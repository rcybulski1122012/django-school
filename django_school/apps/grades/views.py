from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView

from django_school.apps.classes.models import Class
from django_school.apps.grades.models import Grade
from django_school.apps.lessons.models import Subject

User = get_user_model()

SUCCESS_GRADE_CREATE_MESSAGE = "Grade was added successfully."


class GradeCreateView(PermissionRequiredMixin, SuccessMessageMixin, CreateView):
    model = Grade
    fields = ("grade", "weight", "comment", "subject", "student")
    permission_required = "grades.add_grade"
    success_message = SUCCESS_GRADE_CREATE_MESSAGE

    def get_form_kwargs(self):
        form_kwargs = super().get_form_kwargs()
        form_kwargs["initial"] = {
            "subject": self.request.GET.get("subject"),
            "student": self.request.GET.get("student"),
        }

        return form_kwargs

    def get_form(self, **kwargs):
        form = super().get_form(**kwargs)
        slug = self.kwargs["slug"]
        school_class = get_object_or_404(Class, slug=slug)

        taught_subjects = Subject.objects.filter(
            lessons__teacher=self.request.user, lessons__school_class=school_class
        ).distinct()
        taught_classes_students = User.objects.filter(school_class=school_class)

        if not taught_subjects.exists():
            raise PermissionDenied

        form.fields["subject"].queryset = taught_subjects
        form.fields["student"].queryset = taught_classes_students

        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["slug"] = self.kwargs["slug"]

        return context

    def get_success_url(self):
        return reverse("classes:list")
