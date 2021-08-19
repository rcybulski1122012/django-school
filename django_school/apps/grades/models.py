from django.conf import settings
from django.db import models

from django_school.apps.lessons.models import Subject


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
