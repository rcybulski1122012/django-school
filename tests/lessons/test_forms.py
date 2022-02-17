from unittest.mock import MagicMock

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase

from django_school.apps.lessons.forms import (AttendanceFormSet,
                                              LessonSessionForm)
from django_school.apps.lessons.models import AttachedFile
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class AttendanceFormSetTestCase(ClassesMixin, UsersMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.subject = self.create_subject()
        self.student = self.create_student(
            first_name="StudentFirstName",
            last_name="StudentLastName",
            school_class=self.school_class,
        )
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.lesson_session = self.create_lesson_session(self.lesson)
        self.attendances = self.create_attendance(self.lesson_session, [self.student])

    def get_example_formset_data(self, topic, status):
        return {
            "topic": topic,
            "attendance_set-TOTAL_FORMS": "1",
            "attendance_set-INITIAL_FORMS": "1",
            "attendance_set-0-status": status,
            "attendance_set-0-id": self.attendances[0].pk,
            "attendance_set-0-lesson_session": self.lesson_session.pk,
        }

    def test_valid(self):
        data = self.get_example_formset_data("New Topic", "exempt")
        formset = AttendanceFormSet(data=data, instance=self.lesson_session)

        self.assertTrue(formset.is_valid())

    def test_renders_only_as_many_attendances_form_as_attencances_instances(self):
        students = [
            self.create_user(username=f"username{i}", school_class=self.school_class)
            for i in range(5)
        ]
        self.create_attendance(self.lesson_session, students)
        formset = AttendanceFormSet(instance=self.lesson_session)

        self.assertEqual(len(formset.forms), 6)

    def test_formset_html_does_not_contain_default_label(self):
        formset = AttendanceFormSet(instance=self.lesson_session)

        self.assertNotIn(
            '<label for="id_attendance_set-0-status">Status:</label>',
            formset.as_p(),
        )


class LessonSessionFormTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.lesson_session = self.create_lesson_session(self.lesson)

    def test_saves_files_if_valid(self):
        files = [
            SimpleUploadedFile("file1.txt", b"file_content"),
            SimpleUploadedFile("file2.txt", b"file_content"),
        ]

        request = RequestFactory().get("/")
        request.FILES.getlist = MagicMock(return_value=files)

        form = LessonSessionForm(
            {"topic": "new topic"}, request.FILES, instance=self.lesson_session
        )

        self.assertTrue(form.is_valid())
        _, files = form.save()
        self.assertQuerysetEqual(files, AttachedFile.objects.all())

    def test_does_not_save_any_files_if_not_attached(self):
        form = LessonSessionForm({"topic": "new topic"}, instance=self.lesson_session)

        self.assertTrue(form.is_valid())
        form.save()
        self.assertFalse(AttachedFile.objects.exists())

    def test_init_disables_fields(self):
        form = LessonSessionForm(instance=self.lesson_session, disabled=True)

        for field in form.fields.values():
            self.assertTrue(field.disabled)
