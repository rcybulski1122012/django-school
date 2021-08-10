from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DetailView

from django_school.apps.common.forms import AddressForm
from django_school.apps.users.forms import UserInfoForm

User = get_user_model()

SUCCESS_PROFILE_UPDATE_MESSAGE = "Your profile info has been updated successfully."
SUCCESS_PASSWORD_CHANGE_MESSAGE = "Your password has been changed successfully."


class UserDetailView(PermissionRequiredMixin, DetailView):
    model = User
    permission_required = "users.view_user"
    context_object_name = "user"

    def get_queryset(self):
        return super().get_queryset().select_related("school_class__tutor", "address")


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
                SUCCESS_PROFILE_UPDATE_MESSAGE,
                extra_tags="success",
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
    success_message = SUCCESS_PASSWORD_CHANGE_MESSAGE
