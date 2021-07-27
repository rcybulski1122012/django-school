from django.conf import settings
from django.db import models


class Class(models.Model):
    number = models.CharField(max_length=4)
    tutor = models.OneToOneField(settings.AUTH_USER_MODEL, models.SET_NULL, null=True)

    class Meta:
        verbose_name_plural = "classes"

    def __str__(self):
        return self.number
