from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from django_school.apps.common.models import AttachedFile
from django_school.apps.events.models import Event, EventStatus
from django_school.apps.grades.models import GradeCategory
from django_school.apps.lessons.models import (Attendance, Homework,
                                               HomeworkRealisation,
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
        self.teacher = kwargs.pop("teacher")

        super().__init__(*args, **kwargs)

        if disabled:
            for field in self.fields.values():
                field.disabled = True

    def save(self, commit=True):
        lesson_session = super().save(False)

        if commit:
            lesson_session.save()
            files = [
                AttachedFile(
                    file=file, creator=self.teacher, related_object=lesson_session
                )
                for file in self.files.getlist("attached_files")
            ]
            AttachedFile.objects.bulk_create(files)

        return lesson_session


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


class HomeworkForm(forms.ModelForm):
    attached_files = forms.FileField(
        required=False,
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )

    create_category = forms.BooleanField(initial=True, required=False)

    class Meta:
        model = Homework
        exclude = ["created", "school_class", "subject", "teacher"]
        widgets = {"completion_date": forms.DateInput(attrs={"type": "date"})}

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop("teacher")
        self.subject = kwargs.pop("subject")
        self.school_class = kwargs.pop("school_class")
        super().__init__(*args, **kwargs)

    def clean_completion_date(self):
        completion_date = self.cleaned_data["completion_date"]
        today = timezone.now()

        if completion_date <= today:
            raise ValidationError("The completion date must be in the future")

        return completion_date

    def is_valid(self):
        self.instance.subject = self.subject
        self.instance.school_class = self.school_class
        self.instance.teacher = self.teacher

        return super().is_valid()

    def save(self, commit=True):
        homework = super().save(commit=False)

        if commit:
            homework.save()
            event = Event.objects.create(
                title=f"Homework {self.subject.name}",
                description=homework.title,
                date=homework.completion_date,
                teacher=self.teacher,
                school_class=self.school_class,
            )
            EventStatus.objects.create_multiple(event)
            files = [
                AttachedFile(file=file, creator=self.teacher, related_object=homework)
                for file in self.files.getlist("attached_files")
            ]
            AttachedFile.objects.bulk_create(files)

            if self.cleaned_data["create_category"]:
                GradeCategory.objects.create(
                    name=homework.title,
                    subject=self.subject,
                    school_class=self.school_class,
                )

        return homework


class HomeworkRealisationForm(forms.Form):
    attached_files = forms.FileField(
        required=True,
        widget=forms.ClearableFileInput(attrs={"multiple": True}),
    )

    def __init__(self, **kwargs):
        homework = kwargs.pop("homework")
        student = kwargs.pop("student")
        self.instance = HomeworkRealisation(homework=homework, student=student)

        super().__init__(**kwargs)

    def save(self):
        self.instance.save()

        files = [
            AttachedFile(
                file=file, creator=self.instance.student, related_object=self.instance
            )
            for file in self.files.getlist("attached_files")
        ]
        AttachedFile.objects.bulk_create(files)

        return self.instance
