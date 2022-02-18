from django import forms

from django_school.apps.classes.models import Class
from django_school.apps.events.models import Event, EventStatus


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        exclude = ("created", "teacher")
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

        self.fields["school_class"].queryset = Class.objects.visible_to_user(self.user)

    def is_valid(self):
        self.instance.teacher = self.user
        return super().is_valid()

    def save(self, commit=True):
        event = super().save(commit=False)

        if commit:
            event.save()
            EventStatus.objects.create_multiple(event)

        return event
