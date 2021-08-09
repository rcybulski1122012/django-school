from django.db import models


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
