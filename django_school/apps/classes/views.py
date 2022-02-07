from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from django_school.apps.classes.models import Class
from django_school.apps.common.utils import IsTeacherMixin


class ClassesListView(LoginRequiredMixin, IsTeacherMixin, ListView):
    model = Class
    ordering = ["number"]
    context_object_name = "school_classes"
    template_name = "classes/class_list.html"


class ClassDetailView(LoginRequiredMixin, IsTeacherMixin, DetailView):
    model = Class
    slug_url_kwarg = "class_slug"
    context_object_name = "school_class"
    template_name = "classes/class_detail.html"

    def get_queryset(self):
        return super().get_queryset().with_students()
