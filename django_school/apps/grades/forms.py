from django import forms

from django_school.apps.grades.models import Grade


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = [
            "grade",
            "category",
            "weight",
            "comment",
            "student",
            "subject",
            "teacher",
        ]
        widgets = {
            "subject": forms.HiddenInput(),
            "teacher": forms.HiddenInput(),
        }
