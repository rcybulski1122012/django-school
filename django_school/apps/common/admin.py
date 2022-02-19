from django.contrib import admin

from django_school.apps.common.models import Address, AttachedFile


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ("__str__", "user")


@admin.register(AttachedFile)
class AttachedFileAdmin(admin.ModelAdmin):
    pass
