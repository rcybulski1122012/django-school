from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from django_school.apps.classes.models import Class
from django_school.apps.lessons.models import Lesson, Subject

GRADE_ALREADY_EXISTS_MESSAGE = (
    "You can't add a grade, because a grade with this category,"
    " for this student already exists."
)
CLASS_IS_NOT_LEARNING_SUBJECT_MESSAGE = (
    "You can't create a grade category, because given class "
    "is not learning given subject."
)
TEACHER_NOT_IN_TEACHERS_GROUP_MESSAGE = "Given teacher is not in teachers group."
STUDENT_IN_TEACHERS_GROUP_MESSAGE = "Given student is in teachers group."
STUDENT_IS_NOT_LEARNING_THE_SUBJECT_MESSAGE = "The student is not learning the subject."


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

    def clean(self):
        super().clean()

        if not Lesson.objects.filter(
            school_class=self.school_class, subject=self.subject
        ).exists():
            raise ValidationError(CLASS_IS_NOT_LEARNING_SUBJECT_MESSAGE)


class GradeQuerySet(models.QuerySet):
    def with_nested_resources(self):
        return self.select_related("category", "subject", "student", "teacher")


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
        on_delete=models.CASCADE,
        related_name="grades_added",
    )

    objects = GradeQuerySet.as_manager()

    def __str__(self):
        return f"{self.student}: {self.subject} - {self.grade}"

    def clean(self):
        super().clean()

        if Grade.objects.filter(category=self.category, student=self.student).exists():
            raise ValidationError(GRADE_ALREADY_EXISTS_MESSAGE)

        if not self.teacher.is_teacher:
            raise ValidationError(TEACHER_NOT_IN_TEACHERS_GROUP_MESSAGE)

        if self.student.is_teacher:
            raise ValidationError(STUDENT_IN_TEACHERS_GROUP_MESSAGE)

        if not Lesson.objects.filter(
            school_class=self.student.school_class, subject=self.subject
        ):
            raise ValidationError(STUDENT_IS_NOT_LEARNING_THE_SUBJECT_MESSAGE)
