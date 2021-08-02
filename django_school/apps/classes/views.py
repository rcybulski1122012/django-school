from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView, ListView

from django_school.apps.classes.models import Class


class ClassesListView(PermissionRequiredMixin, ListView):
    model = Class
    ordering = ["number"]
    permission_required = "classes.view_class"
    context_object_name = "school_classes"


class ClassDetailView(PermissionRequiredMixin, DetailView):
    model = Class
    permission_required = "classes.view_class"
    context_object_name = "school_class"

    def get_queryset(self):
        return super().get_queryset().select_related("tutor")
