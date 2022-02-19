from os import path
from shutil import rmtree

from django.test import TestCase, override_settings
from django.urls import reverse

from django_school.apps.common.models import AttachedFile
from tests.utils import (ClassesMixin, LessonsMixin, ResourceViewTestMixin,
                         TeacherViewTestMixin, UsersMixin)


@override_settings(MEDIA_ROOT="temp_dir/")
class AttachedFileDeleteViewTestCase(
    TeacherViewTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "attached_file_delete"

    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.lesson_session = self.create_lesson_session(self.lesson)

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

    def test_deletes_attached_file_instance(self):
        self.login(self.teacher)

        self.client.post(self.get_url())

        self.assertFalse(AttachedFile.objects.exists())

    def test_deletes_file(self):
        self.login(self.teacher)

        self.client.post(self.get_url())

        self.assertFalse(path.exists(self.file.file.path))

    def test_returns_403_if_the_user_is_not_a_creator_of_the_file(self):
        self.login(self.student)

        response = self.client.post(self.get_url())

        self.assertEqual(response.status_code, 403)
