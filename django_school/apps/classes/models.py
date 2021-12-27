from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Class(models.Model):
    number = models.CharField(max_length=4, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    tutor = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        models.SET_NULL,
        null=True,
        related_name="teacher_class",
    )

    class Meta:
        verbose_name_plural = "classes"

    def __str__(self):
        return self.number

    def get_absolute_url(self):
        return reverse("classes:detail", args=[self.slug])

    def get_timetable_url(self):
        return reverse("lessons:class_timetable", args=[self.slug])

    def save(self, **kwargs):
        if not self.slug:
            self.slug = slugify(self.number)
        super().save(**kwargs)

    def clean(self):
        super().clean()

        if self.tutor is not None and not self.tutor.is_teacher:
            raise ValidationError("Tutor is not a teacher.")
