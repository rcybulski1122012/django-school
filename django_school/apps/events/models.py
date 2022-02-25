from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch, Q
from django.urls import reverse
from django.utils import timezone

from django_school.apps.classes.models import Class

User = get_user_model()


class EventQuerySet(models.QuerySet):
    def for_year_and_month(self, year, month):
        return self.filter(date__year=year, date__month=month)

    def visible_to_user(self, user):
        global_events = Q(school_class=None)

        if user.is_teacher:
            return self.filter(global_events | Q(teacher=user))
        elif user.is_student:
            return self.filter(global_events | Q(school_class_id=user.school_class_id))
        elif user.is_parent:
            return self.filter(
                global_events | Q(school_class_id=user.child.school_class_id)
            )

    def with_statuses(self, user):
        qs = self.prefetch_related(
            Prefetch(
                "statuses",
                queryset=EventStatus.objects.filter(user=user),
                to_attr="status",
            )
        )

        return qs


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


class EventStatusManager(models.Manager):
    def create_multiple(self, event):
        users_qs = (
            User.objects.filter(
                Q(school_class_id=event.school_class_id)
                | Q(child__school_class_id=event.school_class_id)
            )
            if event.school_class
            else User.objects.exclude(pk=event.teacher_id)
        )
        statuses = [EventStatus(event=event, user=user) for user in users_qs]
        self.model.objects.bulk_create(statuses)

        return statuses


class EventStatus(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="statuses")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    seen = models.BooleanField(default=False)

    objects = EventStatusManager()
