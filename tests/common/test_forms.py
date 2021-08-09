from django.test import TestCase

from django_school.apps.common.forms import AddressForm


class TestAddressForm(TestCase):
    def test_invalid_form_when_blank_fields(self):
        form = AddressForm(
            data={
                "street": "",
                "building_number": "",
                "apartment_number": "",
                "city": "",
                "zip_code": "",
                "country": "",
            }
        )

        self.assertFalse(form.is_valid())

    def test_valid_without_apartment_number(self):
        form = AddressForm(
            data={
                "street": "street",
                "building_number": "15a",
                "apartment_number": "",
                "city": "Krakow",
                "zip_code": "31-632",
                "country": "Poland",
            }
        )

        self.assertTrue(form.is_valid())

    def test_valid_with_apartment_number(self):
        form = AddressForm(
            data={
                "street": "street",
                "building_number": "15a",
                "apartment_number": "4",
                "city": "Krakow",
                "zip_code": "31-632",
                "country": "Poland",
            }
        )

        self.assertTrue(form.is_valid())
