from django import forms
from django.forms import inlineformset_factory

from django_school.apps.lessons.models import LessonSession, Presence


class LessonSessionForm(forms.ModelForm):
    class Meta:
        model = LessonSession
        fields = ["topic"]


class PresenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ["status"]


PresenceFormSet = inlineformset_factory(
    LessonSession,
    Presence,
    fields=("status",),
    can_delete=False,
    max_num=0,
    labels={"status": ""},
)
