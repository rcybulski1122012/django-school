import datetime

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory, TestCase
from django.utils.datastructures import MultiValueDict

from django_school.apps.events.models import Event, EventStatus
from django_school.apps.grades.models import GradeCategory
from django_school.apps.lessons.forms import (AttendanceFormSet, HomeworkForm,
                                              HomeworkRealisationForm,
                                              LessonSessionForm)
from django_school.apps.lessons.models import (AttachedFile, Homework,
                                               HomeworkRealisation)
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class AttendanceFormSetTestCase(ClassesMixin, UsersMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.subject = cls.create_subject()
        cls.student = cls.create_student(
            first_name="StudentFirstName",
            last_name="StudentLastName",
            school_class=cls.school_class,
        )
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.lesson_session = cls.create_lesson_session(cls.lesson)
        cls.attendances = cls.create_attendance(cls.lesson_session, [cls.student])

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

    def test_renders_only_as_many_attendances_form_as_attendance_instances(self):
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
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.lesson_session = cls.create_lesson_session(cls.lesson)

    def test_saves_files_if_valid(self):
        request = RequestFactory().get("/get")
        request.FILES["attached_files"] = SimpleUploadedFile(
            "file1.txt", b"file_content"
        )
        request.FILES["attached_files"] = SimpleUploadedFile(
            "file2.txt", b"file_content"
        )
        form = LessonSessionForm(
            {"topic": "new topic"},
            files=request.FILES,
            instance=self.lesson_session,
            teacher=self.teacher,
        )

        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(AttachedFile.objects.exists())

    def test_init_disables_fields_if_disabled_is_True(self):
        form = LessonSessionForm(
            instance=self.lesson_session, disabled=True, teacher=self.teacher
        )

        for field in form.fields.values():
            self.assertTrue(field.disabled)


class HomeworkFormTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.date = datetime.datetime.today() + datetime.timedelta(days=10)
        cls.files = MultiValueDict()
        cls.files["attached_files"] = SimpleUploadedFile("file2.txt", b"file_content")

    def test_is_valid_assigns_class_subject_and_teacher_to_instance(
        self,
    ):
        form = HomeworkForm(
            subject=self.subject, school_class=self.school_class, teacher=self.teacher
        )

        form.is_valid()

        self.assertEqual(form.instance.subject, self.subject)
        self.assertEqual(form.instance.school_class, self.school_class)
        self.assertEqual(form.instance.teacher, self.teacher)

    def test_save_creates_event_gradecategory_statuses_and_files(self):
        data = {
            "title": "Title",
            "description": "Description",
            "completion_date": self.date,
            "create_category": True,
        }
        form = HomeworkForm(
            data=data,
            files=self.files,
            subject=self.subject,
            school_class=self.school_class,
            teacher=self.teacher,
        )
        form.is_valid()
        form.save()

        self.assertTrue(Homework.objects.exists())
        self.assertTrue(Event.objects.exists())
        self.assertTrue(EventStatus.objects.exists())
        self.assertTrue(AttachedFile.objects.exists())
        self.assertTrue(GradeCategory.objects.exists())

    def test_form_has_error_if_completion_date_is_in_past(self):
        data = {
            "title": "Title",
            "description": "Description",
            "completion_date": self.date + datetime.timedelta(days=-100),
            "create_category": False,
        }

        form = HomeworkForm(
            data=data,
            files=self.files,
            subject=self.subject,
            school_class=self.school_class,
            teacher=self.teacher,
        )

        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors["completion_date"],
            ["The completion date must be in the future"],
        )


class HomeworkRealisationFormTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.homework = cls.create_homework(cls.subject, cls.teacher, cls.school_class)
        cls.files = MultiValueDict()
        cls.files["attached_files"] = SimpleUploadedFile("file2.txt", b"file_content")

    def test_save_creates_realisation_and_attached_files(self):
        form = HomeworkRealisationForm(
            files=self.files, homework=self.homework, student=self.student
        )

        self.assertTrue(form.is_valid())
        form.save()
        self.assertTrue(HomeworkRealisation.objects.exists())
        self.assertTrue(AttachedFile.objects.exists())
