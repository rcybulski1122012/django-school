from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

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
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            None,
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "email",
                    "personal_id",
                    "phone_number",
                    "gender",
                    "address",
                    "school_class",
                    "slug",
                    "role",
                )
            },
        ),
    )
