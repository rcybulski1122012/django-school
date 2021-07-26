from django.test import TestCase

from django_school.apps.common.models import Address


class TestAddressModel(TestCase):
    def test_dunder_str_with_apartment_number(self):
        address = Address(
            street="Nowohucka",
            building_number="12a",
            apartment_number="34",
            city="Krakow",
            zip_code="33-333",
            country="Poland",
        )
        expected = "Nowohucka 12a/34, Krakow 33-333"

        self.assertEqual(str(address), expected)

    def test_dunder_str_without_apartment_number(self):
        address = Address(
            street="Nowohucka",
            building_number="12a",
            city="Krakow",
            zip_code="33-333",
            country="Poland",
        )
        expected = "Nowohucka 12a, Krakow 33-333"

        self.assertEqual(str(address), expected)
