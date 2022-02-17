from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Prefetch
from django.urls import reverse
from django.utils.text import slugify

from django_school.apps.classes.models import Class


class SubjectQuerySet(models.QuerySet):
    def with_does_the_teacher_teach_the_subject_to_the_class(
        self, teacher, school_class
    ):
        return self.prefetch_related(
            Prefetch(
                "lessons",
                queryset=Lesson.objects.filter(
                    teacher=teacher, school_class=school_class
                ),
                to_attr="does_the_teacher_teach_the_subject_to_the_class",
            )
        )


class Subject(models.Model):
    name = models.CharField(max_length=64)
    slug = models.SlugField(max_length=64, unique=True)

    objects = SubjectQuerySet.as_manager()

    def __str__(self):
        return self.name

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(**kwargs)


class Lesson(models.Model):
    LESSONS_TIMES = [
        ("1", "7:00 - 7:45"),
        ("2", "7:50 - 8:35"),
        ("3", "8:45 - 9:30"),
        ("4", "9:40 - 10:25"),
        ("5", "10:45 - 11:30"),
        ("6", "11:40 - 12:25"),
        ("7", "12:35 - 13:20"),
        ("8", "13:30 - 14:15"),
        ("9", "14:25 - 15:10"),
        ("10", "15:20 - 16:05"),
        ("11", "16:15 - 17:00"),
    ]

    WEEKDAYS = [
        ("mon", "Monday"),
        ("tue", "Tuesday"),
        ("wed", "Wednesday"),
        ("thu", "Thursday"),
        ("fri", "Friday"),
        ("sat", "Saturday"),
        ("sun", "Sunday"),
    ]

    time = models.CharField(max_length=32, choices=LESSONS_TIMES)
    weekday = models.CharField(max_length=32, choices=WEEKDAYS)
    classroom = models.PositiveIntegerField()
    subject = models.ForeignKey(
        Subject, on_delete=models.CASCADE, related_name="lessons"
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="lessons"
    )
    school_class = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="lessons"
    )

    def __str__(self):
        return (
            f"{self.school_class}: {self.subject.name}, "
            f"{self.get_weekday_display()}: {self.get_time_display()}"
        )

    def clean(self):
        super().clean()

        if Lesson.objects.filter(
            time=self.time, weekday=self.weekday, teacher=self.teacher
        ).exists():
            raise ValidationError(
                "The teacher can't have two lessons at the same time."
            )

        if not self.teacher.is_teacher:
            raise ValidationError("The teacher is not a teacher.")


class LessonSessionQuerySet(models.QuerySet):
    def visible_to_user(self, user):
        if user.is_teacher:
            return self.filter(lesson__teacher=user)
        elif user.is_student:
            return self.filter(lesson__school_class__students=user)
        else:
            return self.none()

    def with_related_objects(self):
        return self.select_related(
            "lesson__teacher",
            "lesson__school_class",
            "lesson__subject",
        )


class LessonSession(models.Model):
    topic = models.CharField(max_length=128, blank=True, null=True)
    date = models.DateField(null=True)

    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="sessions"
    )
    attendances = models.ManyToManyField(
        settings.AUTH_USER_MODEL, through="lessons.Attendance"
    )

    objects = LessonSessionQuerySet.as_manager()

    def __str__(self):
        return (
            f"{self.lesson.subject.name} {self.lesson.school_class.number}, {self.date}"
        )

    @property
    def detail_url(self):
        return reverse("lessons:session_detail", args=[self.pk])


class AttachedFile(models.Model):
    file = models.FileField(upload_to="lesson_files/")
    lesson_session = models.ForeignKey(
        LessonSession, on_delete=models.CASCADE, related_name="attached_files"
    )

    def __str__(self):
        return self.file.name

    @property
    def delete_url(self):
        return reverse("lessons:attached_file_delete", args=[self.pk])


class Attendance(models.Model):
    ATTENDANCE_STATUSES = [
        ("present", "Present"),
        ("absent", "Absent"),
        ("exempt", "Exempt"),
        ("excused", "Excused"),
        ("none", "None"),
    ]

    student = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    lesson_session = models.ForeignKey(LessonSession, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=16, choices=ATTENDANCE_STATUSES, default="none"
    )

    def clean(self):
        super().clean()

        if self.student.school_class != self.lesson_session.lesson.school_class:
            raise ValidationError("The student is not in class of the lesson session.")
