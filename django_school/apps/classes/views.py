from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.views.generic import DetailView, ListView

from django_school.apps.classes.models import Class


class ClassesListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Class
    ordering = ["number"]
    permission_required = "classes.view_class"
    context_object_name = "classes"


class ClassDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Class
    permission_required = "classes.view_class"
    context_object_name = "class"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("students__user")
            .prefetch_related("tutor")
        )
