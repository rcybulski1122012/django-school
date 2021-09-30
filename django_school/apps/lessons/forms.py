from django import forms

from django_school.apps.lessons.models import (AttachedFile, LessonSession,
                                               Presence)


class LessonSessionForm(forms.ModelForm):
    attached_files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )

    class Meta:
        model = LessonSession
        fields = ["topic"]

    def save(self, commit=True, request_files=None):
        lesson_session = super().save(commit)

        files = (
            [
                AttachedFile(file=file)
                for file in request_files.getlist("attached_files")
            ]
            if request_files
            else []
        )

        if commit:
            lesson_session.save()
            for file in files:
                file.lesson_session = lesson_session

            AttachedFile.objects.bulk_create(files)

        return lesson_session, files


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
