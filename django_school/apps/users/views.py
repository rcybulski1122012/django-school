from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import DetailView

User = get_user_model()


class UserDetailView(PermissionRequiredMixin, DetailView):
    model = User
    permission_required = "users.view_user"
    context_object_name = "user"

    def get_queryset(self):
        return super().get_queryset().select_related("school_class__tutor", "address")
