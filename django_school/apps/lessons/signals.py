import datetime

from django.db.models.signals import pre_save
from django.dispatch import receiver

from django_school.apps.lessons.models import LessonSession


@receiver(pre_save, sender=LessonSession)
def default_date(sender, **kwargs):
    if sender.date is None:
        sender.date = datetime.datetime.today()
