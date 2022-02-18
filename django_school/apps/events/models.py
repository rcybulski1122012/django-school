from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from django_school.apps.classes.models import Class


class EventQuerySet(models.QuerySet):
    def for_year_and_month(self, year, month):
        return self.filter(date__year=year, date__month=month)

    def visible_to_user(self, user):
        global_events = Q(school_class=None)

        if user.is_teacher:
            return self.filter(global_events | Q(teacher=user))
        elif user.is_student:
            return self.filter(global_events | Q(school_class=user.school_class))
        elif user.is_parent:
            return self.filter(global_events | Q(school_class=user.child.school_class))


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
    # if none, the event is global
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

    @property
    def update_url(self):
        return reverse("events:update", args=[self.pk])

    @property
    def delete_url(self):
        return reverse("events:delete", args=[self.pk])
