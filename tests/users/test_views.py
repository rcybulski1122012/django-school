from django.test import TestCase
from django.urls import reverse

from django_school.apps.users.models import Note
from tests.utils import (AjaxRequiredTestMixin, ClassesMixin, CommonMixin,
                         LessonsMixin, LoginRequiredTestMixin,
                         ResourceViewTestMixin, RolesRequiredTestMixin,
                         UsersMixin)


class StudentDetailViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    CommonMixin,
    TestCase,
):
    path_name = "users:detail"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class(tutor=cls.teacher)
        cls.address = cls.create_address()
        cls.student = cls.create_student(
            username="Student",
            school_class=cls.school_class,
            phone_number="TestNumber",
            email="TestEmailAddr@gmail.com",
            address=cls.address,
            first_name="TestFirst",
            last_name="TestLast",
        )
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)

    def get_url(self, user_slug=None):
        user_slug = user_slug or self.student.slug

        return reverse(self.path_name, args=[user_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(user_slug="does-not-exist")

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_returns_404_if_user_is_teacher(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(self.teacher.slug))

        self.assertEqual(response.status_code, 404)

    def test_returns_404_if_user_does_not_teach_student(self):
        self.login(self.teacher)
        student2 = self.create_student(username="student2", slug="student2")

        response = self.client.get(self.get_url(user_slug=student2.slug))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_student(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertEqual(response.context["student"], self.student)

    def test_renders_user_information(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.school_class.number)
        self.assertContains(response, "TestNumber")
        self.assertContains(response, "TestEmailAddr@gmail.com")
        self.assertContains(response, self.student.full_name)
        self.assertContains(response, str(self.address))

    def test_renders_user_notes_given_by_teacher(self):
        self.login(self.teacher)
        note = "The student was talking to a classmate during the lesson"
        self.create_note(self.student, self.teacher, note=note)

        response = self.client.get(self.get_url())

        self.assertContains(response, note)

    def test_renders_appropriate_message_if_student_has_not_any_notes(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, "The student has not received any note yet.")


class PasswordChangeWithMessageViewTestCase(
    LoginRequiredTestMixin, UsersMixin, TestCase
):
    path_name = "users:password_change"

    @classmethod
    def setUpTestData(cls):
        cls.user = cls.create_student()

    def get_url(self):
        return reverse(self.path_name)

    def get_permitted_user(self):
        return None

    def test_displays_success_message(self):
        self.login(self.user)
        data = {
            "old_password": self.DEFAULT_PASSWORD,
            "new_password1": "NewPassword1!",
            "new_password2": "NewPassword1!",
        }

        response = self.client.post(self.get_url(), data, follow=True)

        self.assertContains(response, "The password has been changed successfully.")


class NoteCreateViewTestCase(
    RolesRequiredTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "users:add_note"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)

    def get_url(self, student_id=None):
        url = reverse(self.path_name)
        if student_id:
            return f"{url}?student={student_id}"
        return url

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def get_example_form_data(self):
        return {"student": self.student.id, "note": self.DEFAULT_NOTE}

    def test_sets_student_initial_data_if_given(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url(student_id=self.student.id))

        form_initial = response.context["form"].initial
        self.assertEqual(form_initial["student"], str(self.student.id))

    def test_creates_note(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        self.client.post(self.get_url(), data=data)

        self.assertTrue(Note.objects.exists())

    def test_redirect_to_student_detail_view_after_successful_creation(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data=data)

        self.assertRedirects(response, self.student.student_detail_url)

    def test_renders_success_message_after_successful_creation(self):
        self.login(self.teacher)
        data = self.get_example_form_data()

        response = self.client.post(self.get_url(), data=data, follow=True)

        self.assertContains(response, "The note has been created successfully")


class NoteDeleteViewTestCase(
    RolesRequiredTestMixin,
    ResourceViewTestMixin,
    AjaxRequiredTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "users:note_delete"
    ajax_required = True

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher()
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.note = cls.create_note(cls.student, cls.teacher)

    def get_url(self, note_pk=None):
        note_pk = note_pk or self.note.pk

        return reverse(self.path_name, args=[note_pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(note_pk=12345)

    def get_permitted_user(self):
        return self.teacher

    def get_not_permitted_user(self):
        return self.student

    def test_returns_404_if_teacher_is_not_creator_of_note(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.ajax_request(self.get_url())

        self.assertEqual(response.status_code, 404)

    def test_deletes_note(self):
        self.login(self.teacher)

        self.ajax_request(self.get_url(), method="post")

        self.assertFalse(Note.objects.exists())

    def test_redirects_to_student_detail_view_after_successful_delete(self):
        self.login(self.teacher)

        response = self.ajax_request(self.get_url(), method="post")

        self.assertRedirects(response, self.student.student_detail_url)


class NoteListViewTestCase(
    RolesRequiredTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "users:note_list"

    @classmethod
    def setUpTestData(cls):
        cls.teacher = cls.create_teacher(first_name="FirstName", last_name="LastName")
        cls.school_class = cls.create_class()
        cls.student = cls.create_student(school_class=cls.school_class)
        cls.parent = cls.create_parent(child=cls.student)
        cls.subject = cls.create_subject()
        cls.lesson = cls.create_lesson(cls.subject, cls.teacher, cls.school_class)
        cls.note = cls.create_note(cls.student, cls.teacher, note="NoteNote")

    def get_url(self):
        return reverse(self.path_name)

    def get_permitted_user(self):
        return self.student

    def get_not_permitted_user(self):
        return self.teacher

    def test_renders_notes_info(self):
        self.login(self.student)

        response = self.client.get(self.get_url())

        self.assertContains(response, self.note.note)
        self.assertContains(response, self.note.teacher.full_name)

    def test_context_contains_visible_for_user_notes_ordered_by_created_datetime(self):
        self.login(self.parent)
        student2 = self.create_student(
            username="student2", school_class=self.school_class
        )
        self.create_note(student2, self.teacher)
        note2 = self.create_note(self.student, self.teacher)

        response = self.client.get(self.get_url())

        qs = response.context["notes"]
        self.assertQuerysetEqual(qs, [note2, self.note])

    def test_render_appropriate_message_depended_on_user_role_if_any_note_does_not_exist(
        self,
    ):
        self.note.delete()

        self.login(self.student)
        response = self.client.get(self.get_url())
        self.assertContains(response, "You have not received any notes yet.")

        self.login(self.parent)
        response = self.client.get(self.get_url())
        self.assertContains(response, "Your child has not received any notes yet.")

    def test_renders_paginator_if_there_are_more_than_10_notes(self):
        self.login(self.student)
        for _ in range(10):
            self.create_note(self.student, self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, '<ul class="pagination">')

    def test_sets_notes_seen_by_student_attr_to_True_if_user_is_student(self):
        self.assertFalse(self.note.seen_by_student)
        self.login(self.student)

        self.client.get(self.get_url())
        self.note.refresh_from_db()

        self.assertTrue(self.note.seen_by_student)

    def test_sets_notes_seen_by_parent_attr_to_True_if_user_is_parent(self):
        self.assertFalse(self.note.seen_by_parent)
        self.login(self.parent)

        self.client.get(self.get_url())
        self.note.refresh_from_db()

        self.assertTrue(self.note.seen_by_parent)
