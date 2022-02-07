import datetime

from django.db.models.signals import pre_save
from django.dispatch import receiver

from django_school.apps.lessons.models import LessonSession


@receiver(pre_save, sender=LessonSession)
def default_date(sender, instance, **kwargs):
    if instance.date is None:
        instance.date = datetime.datetime.today()
