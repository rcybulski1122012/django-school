from django import forms

from django_school.apps.common.models import Address


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = "__all__"
