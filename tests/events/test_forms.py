import datetime

from django.test import TestCase

from django_school.apps.classes.models import Class
from django_school.apps.events.forms import EventForm
from tests.utils import ClassesMixin, EventsMixin, LessonsMixin, UsersMixin


class EventFormTestCase(UsersMixin, ClassesMixin, LessonsMixin, EventsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.date = datetime.date.today() + datetime.timedelta(days=1)
        self.event = self.create_event(self.teacher, self.school_class, self.date)

    def test_init_sets_given_user(self):
        form = EventForm(user=self.teacher)

        self.assertEqual(form.user, self.teacher)

    def test_classes_queryset(self):
        subject = self.create_subject()
        teacher2 = self.create_teacher(username="teacher2")
        school_class2 = self.create_class(number="2c")
        self.create_lesson(subject, self.teacher, self.school_class)
        self.create_lesson(subject, teacher2, school_class2)

        form = EventForm(user=teacher2)

        self.assertQuerysetEqual(
            form.fields["school_class"].queryset,
            Class.objects.visible_to_user(teacher2),
        )

    def test_is_valid_assign_teacher_to_an_instance(self):
        form = EventForm(
            user=self.teacher,
        )

        form.is_valid()

        self.assertEqual(form.instance.teacher, self.teacher)
