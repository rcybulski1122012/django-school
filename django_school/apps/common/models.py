from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse


class Address(models.Model):
    street = models.CharField(max_length=128)
    building_number = models.CharField(max_length=16)
    apartment_number = models.CharField(max_length=16, null=True, blank=True)
    city = models.CharField(max_length=128)
    zip_code = models.CharField(max_length=16)
    country = models.CharField(max_length=64)

    class Meta:
        verbose_name_plural = "addresses"

    def __str__(self):
        result = f"{self.street} {self.building_number}"
        result += f"/{self.apartment_number}, " if self.apartment_number else ", "
        result += f"{self.city} {self.zip_code}"

        return result


class AttachedFile(models.Model):
    file = models.FileField(upload_to="attached_files/")
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    related_object_content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE
    )
    related_object_id = models.PositiveIntegerField()
    related_object = GenericForeignKey(
        "related_object_content_type",
        "related_object_id",
    )

    def __str__(self):
        return self.file.name

    @property
    def delete_url(self):
        return reverse("attached_file_delete", args=[self.pk])
