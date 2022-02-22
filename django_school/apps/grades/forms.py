from django import forms
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator

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
        ]

    def __init__(self, *args, **kwargs):
        school_class = kwargs.pop("school_class")
        self.subject = kwargs.pop("subject")
        self.teacher = kwargs.pop("teacher")
        super().__init__(*args, **kwargs)

        self.fields["student"].queryset = User.objects.filter(school_class=school_class)
        self.fields["category"].queryset = GradeCategory.objects.filter(
            subject=self.subject, school_class=school_class
        )

    def is_valid(self):
        self.instance.subject = self.subject
        self.instance.teacher = self.teacher
        return super().is_valid()


class BulkGradeCreationCommonInfoForm(forms.Form):
    weight = forms.IntegerField(
        validators=[MinValueValidator(1, "Weight must be a positive number.")],
        required=True,
    )
    comment = forms.CharField(required=False, widget=forms.Textarea())


class BulkGradeCreationForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ["grade"]


class BaseBulkGradeCreationFormSet(forms.BaseModelFormSet):
    def __init__(self, *args, **kwargs):
        self.students = kwargs.pop("students")
        super().__init__(*args, **kwargs)
        self.queryset = self.model.objects.none()

    def total_form_count(self):
        return len(self.students)

    def _construct_form(self, i, **kwargs):
        form = super()._construct_form(i, **kwargs)
        form.instance.student = self.students[i]
        form.student_label = self.students[i].full_name

        return form

    def set_common_data(self, common_data):
        for form in self.forms:
            for key, value in common_data.items():
                setattr(form.instance, key, value)


BulkGradeCreationFormSet = forms.modelformset_factory(
    Grade,
    form=BulkGradeCreationForm,
    labels={"grade": ""},
    formset=BaseBulkGradeCreationFormSet,
)


class GradeCategoryForm(forms.ModelForm):
    class Meta:
        model = GradeCategory
        fields = ["name"]

    def __init__(self, *args, **kwargs):
        self.subject = kwargs.pop("subject")
        self.school_class = kwargs.pop("school_class")

        super().__init__(*args, **kwargs)

    def is_valid(self):
        self.instance.subject = self.subject
        self.instance.school_class = self.school_class

        return super().is_valid()
