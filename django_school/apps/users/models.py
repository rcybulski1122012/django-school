from django.contrib.auth.models import AbstractUser
from django.db import models

from django_school.apps.classes.models import Class
from django_school.apps.common.models import Address

GENDER_CHOICES = [
    ("male", "male"),
    ("female", "female"),
    ("other", "other"),
]


class User(AbstractUser):
    personal_id = models.CharField(max_length=16, null=True, blank=True)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    gender = models.CharField(
        max_length=16, choices=GENDER_CHOICES, null=True, blank=True
    )

    address = models.OneToOneField(Address, models.SET_NULL, null=True, blank=True)
    school_class = models.ForeignKey(
        Class, models.SET_NULL, null=True, blank=True, related_name="students"
    )
