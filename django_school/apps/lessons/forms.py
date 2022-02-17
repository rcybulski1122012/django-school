from django import forms

from django_school.apps.lessons.models import (AttachedFile, Attendance,
                                               LessonSession)


class LessonSessionForm(forms.ModelForm):
    attached_files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )

    class Meta:
        model = LessonSession
        fields = ["topic"]

    def __init__(self, *args, **kwargs):
        disabled = kwargs.pop("disabled", False)

        super().__init__(*args, **kwargs)

        if disabled:
            for field in self.fields.values():
                field.disabled = True

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


class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ["status"]


class BaseAttendanceFormSet(forms.BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.queryset = self.queryset.select_related("student")


AttendanceFormSet = forms.inlineformset_factory(
    LessonSession,
    Attendance,
    fields=("status",),
    can_delete=False,
    max_num=0,
    labels={"status": ""},
    formset=BaseAttendanceFormSet,
)
