from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone

from django_school.apps.classes.models import Class


class EventQuerySet(models.QuerySet):
    def for_year_and_month(self, year, month):
        return self.filter(date__year=year, date__month=month)

    def for_user(self, user):
        return self.filter(
            Q(teacher=user)
            | Q(school_class_id=user.school_class_id)
            | Q(school_class=None)
        )


class Event(models.Model):
    title = models.CharField(max_length=32)
    description = models.TextField(max_length=256, blank=True, null=True)
    date = models.DateField()
    created = models.DateTimeField(auto_now_add=True)

    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_events",
    )
    school_class = models.ForeignKey(
        Class,
        on_delete=models.SET_NULL,
        related_name="events",
        blank=True,
        null=True,
    )

    objects = EventQuerySet.as_manager()

    def clean(self):
        super().clean()

        if self.date < timezone.now().date():
            raise ValidationError("The date must be in the future.")

        if not self.teacher.is_teacher:
            raise ValidationError("Teacher is not a teacher.")

    @property
    def is_global(self):
        return self.school_class is None
