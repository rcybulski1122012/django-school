from django.test import TestCase

from django_school.apps.users.forms import (NoteForm,
                                            SetPasswordWithActivationForm)
from tests.utils import ClassesMixin, LessonsMixin, UsersMixin


class NoteFormTestCase(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)

    def test_student_queryset(self):
        self.create_student(username="student2")

        form = NoteForm(teacher=self.teacher)
        qs = form.fields["student"].queryset

        self.assertQuerysetEqual(qs, [self.student])

    def test_is_valid_assigns_teacher_to_instance(self):
        form = NoteForm(teacher=self.teacher)

        form.is_valid()

        self.assertEqual(form.instance.teacher, self.teacher)


class SetPasswordWithActivationFormTestCase(UsersMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_user(is_active=False)

    def test_save_activates_account(self):
        form = SetPasswordWithActivationForm(
            data={
                "new_password1": "NewPassword123!",
                "new_password2": "NewPassword123!",
            },
            user=self.user,
        )
        form.is_valid()

        self.assertFalse(self.user.is_active)

        form.save()

        self.assertTrue(self.user.is_active)
