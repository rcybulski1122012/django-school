from os import path
from shutil import rmtree

from django.test import TestCase, override_settings
from django.urls import reverse

from django_school.apps.common.models import AttachedFile
from tests.utils import (AjaxRequiredTestMixin, ClassesMixin, LessonsMixin,
                         ResourceViewTestMixin, RolesRequiredTestMixin,
                         UsersMixin)


@override_settings(MEDIA_ROOT="temp_dir/")
class AttachedFileDeleteViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    AjaxRequiredTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "attached_file_delete"
    ajax_required = True

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.lesson_session = cls.create_lesson_session(cls.lesson)

    def setUp(self):
        self.file = self.create_file(
            related_object=self.lesson_session, creator=self.teacher
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        rmtree("temp_dir/")

    def get_url(self, file_pk=None):
        file_pk = file_pk or self.file.pk

        return reverse(self.path_name, args=[file_pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(file_pk=12345)

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_returns_403_if_user_is_not_creator_of_file(self):
        self.login(self.student)

        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, 403)

    def test_returns_404_if_file_does_not_exist(self):
        self.login(self.teacher)

        response = self.client.post(self.get_url(file_pk=12345))

        self.assertEqual(response.status_code, 404)

    def test_deletes_attached_file_instance(self):
        self.login(self.teacher)

        self.client.post(self.get_url())

        self.assertFalse(AttachedFile.objects.exists())

    def test_deletes_file(self):
        self.login(self.teacher)

        self.client.post(self.get_url())

        self.assertFalse(path.exists(self.file.file.path))
