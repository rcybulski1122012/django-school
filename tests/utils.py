from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django_school.apps.classes.models import Class
from django_school.apps.common.models import Address
from django_school.apps.lessons.models import Lesson, LessonSession, Subject

User = get_user_model()


class UsersMixin:
    fixtures = ["groups.json"]
    DEFAULT_USERNAME = "username"
    DEFAULT_PASSWORD = "password"

    @classmethod
    def create_user(cls, username=DEFAULT_USERNAME, **kwargs):
        return User.objects.create_user(
            username=username, password=cls.DEFAULT_PASSWORD, **kwargs
        )

    def login(self, user):
        return self.client.login(username=user.username, password=self.DEFAULT_PASSWORD)

    def logout(self):
        self.client.logout()

    @staticmethod
    def add_user_to_group(user, group_name):
        group = Group.objects.get(name=group_name)
        user.groups.add(group)

    @classmethod
    def create_teacher(cls, username=DEFAULT_USERNAME, **kwargs):
        teacher = cls.create_user(username, **kwargs)
        cls.add_user_to_group(teacher, "teachers")

        return teacher

    def assertRedirectsWhenNotLoggedIn(self, url, method="get"):
        expected_url = f"{settings.LOGIN_URL}?next={url}"
        method = method.lower()

        response = getattr(self.client, method)(url)

        self.assertRedirects(response, expected_url)


class ClassesMixin:
    DEFAULT_NUMBER = "1a"

    @staticmethod
    def create_class(number=DEFAULT_NUMBER, tutor=None):
        return Class.objects.create(number=number, tutor=tutor)


class CommonMixin:
    DEFAULT_STREET = "street"
    DEFAULT_BUILDING_NUMBER = "1"
    DEFAULT_APARTMENT_NUMBER = "2"
    DEFAULT_CITY = "city"
    DEFAULT_COUNTRY = "country"

    @staticmethod
    def create_address(
        street=DEFAULT_STREET,
        building_number=DEFAULT_BUILDING_NUMBER,
        apartment_number=DEFAULT_APARTMENT_NUMBER,
        city=DEFAULT_CITY,
        country=DEFAULT_COUNTRY,
    ):
        return Address.objects.create(
            street=street,
            building_number=building_number,
            apartment_number=apartment_number,
            city=city,
            country=country,
        )

    def assertContainsFew(self, response, *strings):
        for string in strings:
            self.assertContains(response, string)

    def assertModelFieldsEqual(self, instance, **fields):
        for key, value in fields.items():
            self.assertEqual(getattr(instance, key), value)


class LessonsMixin:
    DEFAULT_SUBJECT_NAME = "subject"
    DEFAULT_TIME = ("1", "7:00 - 7:45")
    DEFAULT_WEEKDAY = ("mon", "Monday")
    DEFAULT_CLASSROOM = 123

    @staticmethod
    def create_subject(name=DEFAULT_SUBJECT_NAME):
        return Subject.objects.create(name=name)

    @staticmethod
    def create_lesson(
        subject,
        teacher,
        school_class,
        time=DEFAULT_TIME,
        weekday=DEFAULT_WEEKDAY,
        classroom=DEFAULT_CLASSROOM,
    ):
        return Lesson.objects.create(
            subject=subject,
            teacher=teacher,
            school_class=school_class,
            time=time,
            weekday=weekday,
            classroom=classroom,
        )

    @staticmethod
    def create_lesson_session(lesson, date=None, **kwargs):
        if date:
            lesson_session = LessonSession.objects.create(lesson=lesson, **kwargs)
            lesson_session.date = date
            lesson_session.save()
        else:
            lesson_session = LessonSession.objects.create(lesson=lesson, **kwargs)

        return lesson_session
