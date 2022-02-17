from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView

from django_school.apps.common.forms import AddressForm
from django_school.apps.common.utils import RolesRequiredMixin
from django_school.apps.users.forms import UserInfoForm
from django_school.apps.users.models import ROLES

User = get_user_model()


class StudentDetailView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER), DetailView
):
    model = User
    slug_url_kwarg = "student_slug"
    template_name = "users/student_detail.html"
    context_object_name = "user"

    def dispatch(self, request, *args, **kwargs):
        if self.is_requested_user_a_teacher():
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def is_requested_user_a_teacher(self):
        return User.objects.filter(
            slug=self.kwargs[self.slug_url_kwarg], role=ROLES.TEACHER
        ).exists()

    def get_queryset(self):
        return super().get_queryset().select_related("address", "school_class__tutor")


@login_required
def profile_view(request):
    user_info_form = UserInfoForm(request.POST or None, instance=request.user)
    address_form = AddressForm(request.POST or None, instance=request.user.address)

    if request.method == "POST":
        if user_info_form.is_valid() and address_form.is_valid():
            user_info_form.save()
            address_form.save()
            messages.success(
                request,
                "The profile information has been updated successfully.",
            )
            return redirect("users:profile")

    return render(
        request,
        "users/profile.html",
        {"user_info_form": user_info_form, "address_form": address_form},
    )


class PasswordChangeWithMessageView(SuccessMessageMixin, PasswordChangeView):
    success_url = reverse_lazy("users:profile")
    success_message = "The password has been changed successfully."
