from django import forms

from django_school.apps.lessons.models import LessonSession, Presence


class LessonSessionForm(forms.ModelForm):
    class Meta:
        model = LessonSession
        fields = ["topic"]


class PresenceForm(forms.ModelForm):
    class Meta:
        model = Presence
        fields = ["status"]


class BasePresenceFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queryset = self.queryset.select_related("student")


PresenceFormSet = forms.inlineformset_factory(
    LessonSession,
    Presence,
    fields=("status",),
    can_delete=False,
    max_num=0,
    labels={"status": ""},
    formset=BasePresenceFormSet,
)
