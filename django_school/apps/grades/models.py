from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django_school.apps.classes.models import Class
from django_school.apps.lessons.models import Subject

GRADE_ALREADY_EXISTS_MESSAGE = (
    "You can't add a grade, because a grade with this category,"
    " for this student already exists."
)


class GradeCategory(models.Model):
    name = models.CharField(max_length=64)

    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="grades_categories"
    )
    school_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="grades_categories"
    )

    class Meta:
        verbose_name_plural = "grade categories"

    def __str__(self):
        return self.name


class Grade(models.Model):
    GRADES = [
        (1.0, "1"),
        (1.5, "1+"),
        (1.75, "2-"),
        (2.0, "2"),
        (2.5, "2+"),
        (2.75, "3-"),
        (3.0, "3"),
        (3.5, "3+"),
        (3.75, "4-"),
        (4.0, "4"),
        (4.5, "4+"),
        (4.75, "5-"),
        (5.0, "5"),
        (5.5, "5+"),
        (5.75, "6-"),
        (6.0, "6"),
    ]

    grade = models.FloatField(choices=GRADES)
    weight = models.PositiveIntegerField()
    comment = models.TextField(null=True, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    category = models.ForeignKey(
        GradeCategory, on_delete=models.CASCADE, related_name="grades"
    )
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="grades"
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="grades_gotten"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="grades_added",
        null=True,
    )

    def __str__(self):
        return f"{self.student}: {self.subject} - {self.grade}"

    def clean(self):
        super().clean()

        if Grade.objects.filter(category=self.category, student=self.student).exists():
            raise ValidationError(GRADE_ALREADY_EXISTS_MESSAGE)
