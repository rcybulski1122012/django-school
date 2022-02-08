from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.db.models import F, Prefetch, Q, Sum
from django.urls import reverse
from django.utils.text import slugify

from django_school.apps.classes.models import Class
from django_school.apps.common.models import Address
from django_school.apps.grades.models import Grade


class StudentsQuerySet(models.QuerySet):
    def with_weighted_avg(self, subject):
        return self.annotate(
            w_avg=Sum(
                F("grades_gotten__grade") * F("grades_gotten__weight"),
                filter=Q(grades_gotten__subject=subject),
            )
            / Sum(F("grades_gotten__weight"), filter=Q(grades_gotten__subject=subject)),
        )

    def with_subject_grades(self, subject):
        return self.prefetch_related(
            Prefetch(
                "grades_gotten",
                queryset=Grade.objects.filter(subject=subject).select_related(
                    "category"
                ),
                to_attr="subject_grades",
            )
        )

    def visible_to_user(self, user):
        if user.is_teacher:
            return self.filter(school_class__lessons__teacher=user).distinct()
        else:
            return self.filter(pk=user.pk)


class StudentsManager(models.Manager):
    def get_queryset(self):
        return StudentsQuerySet(self.model, using=self._db).filter(role=ROLES.STUDENT)


class TeachersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=ROLES.TEACHER)


class ROLES(models.TextChoices):
    TEACHER = ("TEACHER", "Teacher")
    STUDENT = ("STUDENT", "Student")
    PARENT = ("PARENT", "Parent")


class User(AbstractUser):
    GENDER_CHOICES = [
        ("male", "male"),
        ("female", "female"),
        ("other", "other"),
    ]

    role = models.TextField(null=True, choices=ROLES.choices)
    slug = models.SlugField(max_length=64, unique=True)
    personal_id = models.CharField(max_length=16, null=True, blank=True)
    phone_number = models.CharField(max_length=16, null=True, blank=True)
    gender = models.CharField(
        max_length=16, choices=GENDER_CHOICES, null=True, blank=True
    )

    address = models.OneToOneField(Address, models.SET_NULL, null=True, blank=True)
    school_class = models.ForeignKey(
        Class, models.SET_NULL, null=True, blank=True, related_name="students"
    )

    objects = UserManager()
    students = StudentsManager.from_queryset(StudentsQuerySet)()
    teachers = TeachersManager()

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
        return self.role == ROLES.TEACHER

    @property
    def is_student(self):
        return self.role == ROLES.STUDENT

    @property
    def is_parent(self):
        return self.role == ROLES.PARENT

    @property
    def attendance_url(self):
        return reverse("lessons:student_attendance", args=[self.slug])
