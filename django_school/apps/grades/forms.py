from django import forms
from django.contrib.auth import get_user_model

from django_school.apps.grades.models import Grade, GradeCategory

User = get_user_model()


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

    def __init__(self, *args, **kwargs):
        school_class = kwargs.pop("school_class")
        subject = kwargs.pop("subject")
        super().__init__(*args, **kwargs)

        self.fields["student"].queryset = User.objects.filter(school_class=school_class)
        self.fields["category"].queryset = GradeCategory.objects.filter(
            subject=subject, school_class=school_class
        )
