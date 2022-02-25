from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import DetailView, ListView

from django_school.apps.classes.models import Class
from django_school.apps.common.utils import RolesRequiredMixin
from django_school.apps.users.models import ROLES


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
