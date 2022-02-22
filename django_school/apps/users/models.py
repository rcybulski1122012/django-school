from django.apps import apps
from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Count, F, Prefetch, Q, Sum
from django.urls import reverse
from django.utils.text import slugify

from django_school.apps.classes.models import Class
from django_school.apps.common.models import Address
from django_school.apps.grades.models import Grade


class StudentsQuerySet(models.QuerySet):
    def with_weighted_avg_for_subject(self, subject):
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

    def with_attendance(self, **attendance_params):
        statuses = ["present", "absent", "exempt", "excused"]
        counters = {
            f"{status}_hours": Count(
                "attendance",
                filter=Q(attendance__status=status, **attendance_params),
                distinct=True,
            )
            for status in statuses
        }

        return self.annotate(
            total_attendance=Count(
                "attendance",
                ~Q(attendance__status="none") & Q(**attendance_params),
                distinct=True,
            ),
            **counters,
        )

    def with_homework_realisations(self, homework):
        return (
            self.filter(school_class_id=homework.school_class_id)
            .prefetch_related(
                Prefetch(
                    "homeworks_realisations",
                    queryset=apps.get_model("lessons", "HomeworkRealisation")
                    .objects.filter(homework=homework)
                    .prefetch_related("attached_files"),
                    to_attr="realisation",
                )
            )
            .distinct()
        )

    def exclude_if_has_grade_in_category(self, category):
        return self.annotate(
            has_grade=Count("grades_gotten", filter=Q(grades_gotten__category=category))
        ).exclude(has_grade=1)

    def visible_to_user(self, user):
        if user.is_teacher:
            return self.filter(school_class__lessons__teacher=user).distinct()
        elif user.is_student:
            return self.filter(pk=user.pk)
        elif user.is_parent:
            return self.filter(pk=user.child_id)


class StudentsManager(models.Manager):
    def get_queryset(self):
        return StudentsQuerySet(self.model, using=self._db).filter(role=ROLES.STUDENT)


class TeachersManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(role=ROLES.TEACHER)


class CustomUserManager(UserManager):
    def get(self, *args, **kwargs):
        return (
            super()
            .select_related("child__school_class", "school_class")
            .get(*args, **kwargs)
        )


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
    child = models.OneToOneField(
        "self", models.SET_NULL, null=True, blank=True, related_name="parent"
    )

    objects = CustomUserManager()
    students = StudentsManager.from_queryset(StudentsQuerySet)()
    teachers = TeachersManager()

    def __str__(self):
        return self.full_name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.full_name)
        super().save(**kwargs)

    def clean(self):
        super().clean()

        if not self.is_student and self.school_class is not None:
            raise ValidationError("A class can be assigned only to a student")

        if not self.is_parent and self.child is not None:
            raise ValidationError("A child can be assigned only to a parent")
        elif self.child and not self.child.is_student:
            raise ValidationError("A child must be a student")

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
    def student_detail_url(self):
        return reverse("users:detail", args=[self.slug])

    @property
    def attendance_url(self):
        if self.is_student:
            return reverse("lessons:student_attendance", args=[self.slug])
        elif self.is_parent:
            return reverse("lessons:student_attendance", args=[self.child.slug])

    @property
    def teacher_timetable_url(self):
        return reverse("lessons:teacher_timetable", args=[self.slug])

    @property
    def grades_url(self):
        if self.is_student:
            return reverse("grades:student_grades", args=[self.slug])
        elif self.is_parent:
            return reverse("grades:student_grades", args=[self.child.slug])
