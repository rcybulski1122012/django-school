from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django_school.apps.users.forms import UserCreationWithoutPasswordForm
from django_school.apps.users.token_generator import \
    set_password_token_generator

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    prepopulated_fields = {"slug": ("first_name", "last_name")}
    list_display = ("full_name", "role", "school_class")
    list_filter = ("role", "school_class")
    fieldsets = UserAdmin.fieldsets + (
        (
            None,
            {
                "fields": (
                    "personal_id",
                    "phone_number",
                    "gender",
                    "address",
                    "school_class",
                    "slug",
                )
            },
        ),
    )
    add_fieldsets = (
        (
            None,
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "email",
                    "personal_id",
                    "phone_number",
                    "gender",
                    "address",
                    "school_class",
                    "child",
                    "slug",
                    "role",
                ),
            },
        ),
    )
    add_form = UserCreationWithoutPasswordForm

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        form = PasswordResetForm({"email": obj.email})

        if form.is_valid():
            context = {
                "domain": get_current_site(request).domain,
                "protocol": "http",
                "uid": urlsafe_base64_encode(force_bytes(obj.pk)),
                "token": set_password_token_generator.make_token(obj),
            }

            form.send_mail(
                subject_template_name="registration/password_set_subject.html",
                email_template_name="registration/password_set_email.html",
                context=context,
                from_email=None,
                to_email=obj.email,
            )
