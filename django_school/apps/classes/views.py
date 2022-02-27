from collections import defaultdict

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView
from django.views.generic.detail import SingleObjectMixin
from django_weasyprint import WeasyTemplateView

from django_school.apps.classes.models import Class
from django_school.apps.common.utils import RolesRequiredMixin
from django_school.apps.users.models import ROLES

User = get_user_model()


class ClassListView(LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER), ListView):
    model = Class
    ordering = ["number"]
    template_name = "classes/class_list.html"
    context_object_name = "school_classes"

    def get_queryset(self):
        return super().get_queryset().visible_to_user(self.request.user)


class ClassDetailView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER), DetailView
):
    model = Class
    slug_url_kwarg = "class_slug"
    template_name = "classes/class_detail.html"
    context_object_name = "school_class"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .visible_to_user(self.request.user)
            .with_students()
            .distinct()
        )


class ClassSummaryPDFView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SingleObjectMixin,
    WeasyTemplateView,
):
    model = Class
    slug_url_kwarg = "class_slug"
    template_name = "classes/summary_pdf.html"
    context_object_name = "school_class"

    object = None

    def get_queryset(self):
        return super().get_queryset().filter(tutor=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        students = list(
            User.students.with_attendance()
            .prefetch_related("grades_gotten__subject", "notes_gotten")
            .filter(school_class=self.get_object())
            .order_by("first_name")
        )
        grades_dict = defaultdict(lambda: defaultdict(list))
        for student in students:
            for grade in student.grades_gotten.all():
                grades_dict[student][grade.subject.name].append(
                    grade.get_grade_display()
                )

        ctx["grades_dict"] = dict(grades_dict)
        ctx["last_student"] = students[-1]
        # needed in condition to stop breaking last page
        return ctx
