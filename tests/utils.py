from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.utils.text import slugify

from django_school.apps.classes.models import Class
from django_school.apps.common.models import Address
from django_school.apps.events.models import Event
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import (AttachedFile, Attendance,
                                               Lesson, LessonSession, Subject)
from django_school.apps.messages.models import Message, MessageStatus
from django_school.apps.users.models import ROLES

User = get_user_model()


class UsersMixin:
    DEFAULT_USERNAME = "username"
    DEFAULT_PASSWORD = "password"
    TEACHER_USERNAME = "teacher"
    STUDENT_USERNAME = "student"
    PARENT_USERNAME = "username"

    @classmethod
    def create_user(cls, username=DEFAULT_USERNAME, **kwargs):
        if "slug" not in kwargs:
            kwargs["slug"] = slugify(username)

        return User.objects.create_user(
            username=username,
            password=cls.DEFAULT_PASSWORD,
            **kwargs,
        )

    def login(self, user):
        return self.client.login(username=user.username, password=self.DEFAULT_PASSWORD)

    def logout(self):
        self.client.logout()

    @classmethod
    def create_teacher(cls, username=TEACHER_USERNAME, **kwargs):
        teacher = cls.create_user(username, role=ROLES.TEACHER, **kwargs)

        return teacher

    @classmethod
    def create_student(cls, username=STUDENT_USERNAME, **kwargs):
        student = cls.create_user(username, role=ROLES.STUDENT, **kwargs)

        return student

    @classmethod
    def create_parent(cls, username=PARENT_USERNAME, **kwargs):
        parent = cls.create_user(username, role=ROLES.PARENT, **kwargs)

        return parent

    @classmethod
    def create_superuser(cls, username="superuser", **kwargs):
        superuser = cls.create_user(username, is_superuser=True, **kwargs)

        return superuser


class ClassesMixin:
    DEFAULT_NUMBER = "1a"

    @staticmethod
    def create_class(number=DEFAULT_NUMBER, tutor=None, **kwargs):
        return Class.objects.create(number=number, tutor=tutor, **kwargs)


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
        **kwargs,
    ):
        return Address.objects.create(
            street=street,
            building_number=building_number,
            apartment_number=apartment_number,
            city=city,
            country=country,
            **kwargs,
        )


class LessonsMixin:
    DEFAULT_SUBJECT_NAME = "subject"
    DEFAULT_TIME = ("1", "7:00 - 7:45")
    DEFAULT_WEEKDAY = ("mon", "Monday")
    DEFAULT_CLASSROOM = 123
    DEFAULT_FILE_NAME = "file.txt"

    @staticmethod
    def create_subject(name=DEFAULT_SUBJECT_NAME, **kwargs):
        return Subject.objects.create(name=name, **kwargs)

    @staticmethod
    def create_lesson(
        subject,
        teacher,
        school_class,
        time=DEFAULT_TIME,
        weekday=DEFAULT_WEEKDAY,
        classroom=DEFAULT_CLASSROOM,
        **kwargs,
    ):
        return Lesson.objects.create(
            subject=subject,
            teacher=teacher,
            school_class=school_class,
            time=time,
            weekday=weekday,
            classroom=classroom,
            **kwargs,
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

    @staticmethod
    def create_attendance(lesson_session, students, status="none"):
        attendances = [
            Attendance(lesson_session=lesson_session, student=student, status=status)
            for student in students
        ]

        with transaction.atomic():
            Attendance.objects.bulk_create(attendances)
            return Attendance.objects.order_by("-id")[: len(attendances)]

    @staticmethod
    def create_file(related_object, creator, name=DEFAULT_FILE_NAME):
        file = SimpleUploadedFile(name, b"file_content")

        return AttachedFile.objects.create(
            related_object=related_object, creator=creator, file=file
        )


class GradesMixin:
    DEFAULT_GRADE_CATEGORY_NAME = "Exam"

    DEFAULT_GRADE = "3"
    DEFAULT_WEIGHT = "1"

    @staticmethod
    def create_grade_category(
        subject, school_class, name=DEFAULT_GRADE_CATEGORY_NAME, **kwargs
    ):
        return GradeCategory.objects.create(
            subject=subject, school_class=school_class, name=name, **kwargs
        )

    @staticmethod
    def create_grade(
        category,
        subject,
        student,
        teacher,
        grade=DEFAULT_GRADE,
        weight=DEFAULT_WEIGHT,
        **kwargs,
    ):
        return Grade.objects.create(
            category=category,
            subject=subject,
            student=student,
            teacher=teacher,
            grade=grade,
            weight=weight,
            **kwargs,
        )


class MessagesMixin:
    DEFAULT_TOPIC = "Message Topic"
    DEFAULT_CONTENT = "Message Content"

    @staticmethod
    def create_message(
        sender, receivers, topic=DEFAULT_TOPIC, content=DEFAULT_CONTENT, **kwargs
    ):
        message = Message.objects.create(
            sender=sender, topic=topic, content=content, **kwargs
        )
        statuses = [
            MessageStatus(message=message, receiver=receiver) for receiver in receivers
        ]
        MessageStatus.objects.bulk_create(statuses)

        return message


class EventsMixin:
    DEFAULT_TITLE = "Event Title"
    DEFAULT_DESCRIPTION = "Event Description"

    @staticmethod
    def create_event(
        teacher,
        school_class,
        date,
        title=DEFAULT_TITLE,
        description=DEFAULT_DESCRIPTION,
        **kwargs,
    ):
        return Event.objects.create(
            teacher=teacher,
            school_class=school_class,
            date=date,
            title=title,
            description=description,
            **kwargs,
        )


class LoginRequiredTestMixin:
    ajax_required = False

    def get_url(self):
        raise NotImplementedError("get_url must be overridden")

    def test_redirects_to_login_page_when_user_is_not_logged_in(self):
        expected_url = f"{settings.LOGIN_URL}?next={self.get_url()}"

        params = (
            {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"} if self.ajax_required else {}
        )
        response = self.client.get(self.get_url(), **params)

        self.assertRedirects(response, expected_url)


class TeacherViewTestMixin(LoginRequiredTestMixin):
    ajax_required = False

    def test_returns_403_when_user_is_not_a_teacher(self):
        self.login(self.student)

        params = (
            {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"} if self.ajax_required else {}
        )
        response = self.client.get(self.get_url(), **params)

        self.assertEqual(response.status_code, 403)

    def test_returns_200_when_user_is_a_teacher(self):
        self.login(self.teacher)

        params = (
            {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"} if self.ajax_required else {}
        )
        response = self.client.get(self.get_url(), **params)

        self.assertEqual(response.status_code, 200)


class ResourceViewTestMixin:
    ajax_required = False

    def get_nonexistent_resource_url(self):
        raise NotImplementedError("get_nonexistent_resource_url must be overridden")

    def test_returns_404_if_object_does_not_exist(self):
        mro = super().__self_class__.__mro__

        if TeacherViewTestMixin in mro:
            self.login(self.teacher)
        elif LoginRequiredTestMixin in mro:
            self.login(self.student)

        params = (
            {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"} if self.ajax_required else {}
        )
        response = self.client.get(self.get_nonexistent_resource_url(), **params)

        self.assertEqual(response.status_code, 404)
