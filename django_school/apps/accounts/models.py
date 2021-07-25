from django.conf import settings
from django.db import models

from django_school.apps.classes.models import Class
from django_school.apps.common.models import Address

User = settings.AUTH_USER_MODEL

GENDER_CHOICES = [
    ("male", "male"),
    ("female", "female"),
    ("other", "other"),
]


class Profile(models.Model):
    age = models.PositiveIntegerField()
    personal_id = models.CharField(max_length=16)
    phone_number = models.CharField(max_length=16)
    gender = models.CharField(max_length=16, choices=GENDER_CHOICES)

    user = models.OneToOneField(User, models.CASCADE)
    address = models.OneToOneField(Address, models.SET_NULL, null=True)
    school_class = models.OneToOneField(Class, models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
