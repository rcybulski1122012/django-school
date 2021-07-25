from django.contrib import admin

from django_school.apps.common.models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    pass
