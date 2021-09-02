from django.test import TestCase

from django_school.apps.lessons.forms import PresenceFormSet
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class TestPresenceFormSet(ClassesMixin, UsersMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.subject = self.create_subject()
        self.student = self.create_user(
            username="student123",
            first_name="StudentFirstName",
            last_name="StudentLastName",
            school_class=self.school_class,
        )
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.lesson_session = self.create_lesson_session(self.lesson)
        self.presences = self.create_presences(self.lesson_session, [self.student])

    @staticmethod
    def get_example_formset_data(topic, status):
        return {
            "topic": topic,
            "presence_set-TOTAL_FORMS": "1",
            "presence_set-INITIAL_FORMS": "1",
            "presence_set-0-status": status,
            "presence_set-0-id": "1",
            "presence_set-0-lesson_session": "1",
        }

    def test_valid(self):
        data = self.get_example_formset_data("New Topic", "exempt")
        formset = PresenceFormSet(data=data, instance=self.lesson_session)

        self.assertTrue(formset.is_valid())

    def test_renders_only_as_many_presences_form_as_presences_instances(self):
        students = [
            self.create_user(username=f"username{i}", school_class=self.school_class)
            for i in range(5)
        ]
        self.create_presences(self.lesson_session, students)
        formset = PresenceFormSet(instance=self.lesson_session)

        self.assertEqual(len(formset.forms), 6)

    def test_form_html_does_not_contain_default_label(self):
        formset = PresenceFormSet(instance=self.lesson_session)

        self.assertNotIn(
            '<label for="id_presence_set-0-status">Status:</label>',
            formset.as_p(),
        )
