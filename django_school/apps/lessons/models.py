from django.db import models

from django_school import settings
from django_school.apps.classes.models import Class


class Subject(models.Model):
    name = models.CharField(max_length=64)

    def __str__(self):
        return self.name


LESSONS_TIMES = [
    ("1", "7:00 - 7:45"),
    ("2", "7:50 - 8:35"),
    ("3", "8:45 - 9:30"),
    ("4", "9:40 - 10:25"),
    ("5", "10:45 - 11:30"),
    ("6", "11:40 - 12:25"),
    ("7", "12:35 - 13:20"),
    ("8", "13:30 - 14:15"),
    ("9", "14:25 - 15:10"),
    ("10", "15:20 - 16:05"),
    ("11", "16:15 - 17:00"),
]

WEEKDAYS = [
    ("mon", "Monday"),
    ("tue", "Tuesday"),
    ("wed", "Wednesday"),
    ("thu", "Thursday"),
    ("fri", "Friday"),
    ("sat", "Saturday"),
    ("sun", "Sunday"),
]


class Lesson(models.Model):
    time = models.CharField(max_length=16, choices=LESSONS_TIMES)
    weekday = models.CharField(max_length=16, choices=WEEKDAYS)
    classroom = models.PositiveIntegerField()
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="lessons"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lessons"
    )
    school_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="lessons"
    )

    def __str__(self):
        return f"{self.school_class}: {self.subject.name}, {self.weekday}: {self.time}"
