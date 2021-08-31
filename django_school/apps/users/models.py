from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from django_school.apps.classes.models import Class
from django_school.apps.common.models import Address


class CustomUserManager(UserManager):
    def with_nested_resources(self):
        return super().get_queryset().select_related("address")

    def with_nested_student_resources(self):
        return (
            super()
            .get_queryset()
            .select_related("address", "school_class__tutor")
            .prefetch_related("grades_gotten__category")
        )

    def with_nested_teacher_resources(self):
        return (
            super()
            .get_queryset()
            .select_related("address", "teacher_class")
            .prefetch_related("grades_added__category", "lessons__subject")
        )


class User(AbstractUser):
    GENDER_CHOICES = [
        ("male", "male"),
        ("female", "female"),
        ("other", "other"),
    ]

    slug = models.SlugField(max_length=64, blank=True)
    personal_id = models.CharField(max_length=16, null=True, blank=True)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    gender = models.CharField(
        max_length=16, choices=GENDER_CHOICES, null=True, blank=True
    )

    address = models.OneToOneField(Address, models.SET_NULL, null=True, blank=True)
    school_class = models.ForeignKey(
        Class, models.SET_NULL, null=True, blank=True, related_name="students"
    )

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name

    def get_absolute_url(self):
        return reverse("users:detail", args=[self.slug])

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
        super().save(**kwargs)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def is_teacher(self):
        return self.groups.filter(name="teachers").exists()
