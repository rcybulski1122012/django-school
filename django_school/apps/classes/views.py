from django.contrib.auth.mixins import (LoginRequiredMixin,
                                        PermissionRequiredMixin)
from django.views.generic import ListView

from django_school.apps.classes.models import Class


class ClassesListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Class
    ordering = ["number"]
    permission_required = "classes.view_class"
    context_object_name = "classes"
