from django.conf import settings
from django.db import models
from django.urls import reverse


class Class(models.Model):
    number = models.CharField(max_length=4, unique=True)
    tutor = models.OneToOneField(settings.AUTH_USER_MODEL, models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "classes"

    def get_absolute_url(self):
        return reverse("classes:detail", args=[self.pk])

    def get_timetable_url(self):
        return reverse("lessons:class_timetable", args=[self.pk])

    def __str__(self):
        return self.number
