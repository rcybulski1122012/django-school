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
from django_school.apps.common.utils import IsTeacherMixin
from django_school.apps.users.forms import UserInfoForm

User = get_user_model()


class StudentDetailView(LoginRequiredMixin, IsTeacherMixin, DetailView):
    model = User
    slug_url_kwarg = "student_slug"
    template_name = "users/student_detail.html"
    context_object_name = "user"

    def dispatch(self, request, *args, **kwargs):
        if self.is_the_user_in_teachers_group():
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def is_the_user_in_teachers_group(self):
        return User.objects.filter(
            slug=self.kwargs[self.slug_url_kwarg], groups__name="teachers"
        ).exists()

    def get_queryset(self):
        return super().get_queryset().select_related("address", "school_class__tutor")


@login_required
def profile_view(request):
    if request.method == "POST":
        user_info_form = UserInfoForm(request.POST, instance=request.user)
        address_form = AddressForm(request.POST, instance=request.user.address)
        if user_info_form.is_valid() and address_form.is_valid():
            user_info_form.save()
            address_form.save()
            messages.success(
                request,
                "The profile information has been updated successfully.",
            )
            return redirect("users:profile")
    else:
        user_info_form = UserInfoForm(instance=request.user)
        address_form = AddressForm(instance=request.user.address)

    return render(
        request,
        "users/profile.html",
        {"user_info_form": user_info_form, "address_form": address_form},
    )


class PasswordChangeWithMessageView(SuccessMessageMixin, PasswordChangeView):
    success_url = reverse_lazy("users:profile")
    success_message = "The password has been changed successfully."
