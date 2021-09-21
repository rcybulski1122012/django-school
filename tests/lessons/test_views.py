import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django_school.apps.lessons.models import Lesson, Presence
from tests.utils import (ClassesMixin, LessonsMixin, ResourceViewTestMixin,
                         TeacherViewTestMixin, UsersMixin)


class TimetableViewMixin(
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)

    def test_context_contains_weekdays_and_lessons_times(self):
        response = self.client.get(self.get_url())

        self.assertEqual(response.context["weekdays"], Lesson.WEEKDAYS)
        self.assertEqual(response.context["lessons_times"], Lesson.LESSONS_TIMES)

    def test_renders_lessons(self):
        response = self.client.get(self.get_url())

        self.assertContains(response, self.teacher.full_name)
        self.assertContains(response, self.subject.name)
        self.assertContains(response, self.lesson.classroom)


class ClassTimetableViewTestCase(TimetableViewMixin, TestCase):
    path_name = "lessons:class_timetable"

    def get_url(self, class_slug=None):
        class_slug = class_slug or self.school_class.slug

        return reverse(self.path_name, args=[class_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(class_slug="does-not-exist")

    def test_context_contains_school_class(self):
        response = self.client.get(self.get_url())

        self.assertEqual(response.context["school_class"], self.school_class)


class TeacherTimetableViewTestCase(TimetableViewMixin, TestCase):
    path_name = "lessons:teacher_timetable"

    def get_url(self, teacher_slug=None):
        teacher_slug = teacher_slug or self.teacher.slug

        return reverse(self.path_name, args=[teacher_slug])

    def get_nonexistent_resource_url(self):
        return self.get_url(teacher_slug="does-not-exist")

    def test_returns_404_when_user_is_not_a_teacher(self):
        response = self.client.get(self.get_url(teacher_slug=self.student.slug))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_teacher(self):
        response = self.client.get(self.get_url())

        self.assertEqual(response.context["teacher"], self.teacher)


class TimetablesListViewTestCase(UsersMixin, ClassesMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()

    def test_context_contains_lists_of_classes_and_teachers(self):
        response = self.client.get(reverse("lessons:timetables_list"))

        self.assertQuerysetEqual(
            response.context["school_classes"], [self.school_class]
        )
        self.assertQuerysetEqual(response.context["teachers"], [self.teacher])

    def test_renders_links_to_timetables(self):
        response = self.client.get(reverse("lessons:timetables_list"))

        self.assertContains(
            response, reverse("lessons:class_timetable", args=[self.school_class.slug])
        )
        self.assertContains(
            response, reverse("lessons:teacher_timetable", args=[self.teacher.slug])
        )


class TeacherLessonSessionsListViewTestCase(
    TeacherViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "lessons:session_list"

    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(school_class=self.school_class)
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(
            self.subject,
            self.teacher,
            self.school_class,
            weekday="fri",
        )

    def get_url(self, **kwargs):
        url = reverse(self.path_name)
        if date := kwargs.get("date"):
            return f"{url}?date={date}"
        return url

    def test_selects_only_lesson_sessions_of_currently_logged_teacher(self):
        self.login(self.teacher)
        teacher2 = self.create_teacher(username="SecondTeacher2")
        lesson2 = self.create_lesson(self.subject, teacher2, self.school_class)
        session1 = self.create_lesson_session(self.lesson)
        self.create_lesson_session(lesson2)

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["lesson_sessions"], [session1])

    def test_select_today_lesson_sessions_by_default(self):
        self.login(self.teacher)
        lesson2 = self.create_lesson(
            self.subject, self.teacher, self.school_class, weekday="mon"
        )
        session1 = self.create_lesson_session(self.lesson)
        self.create_lesson_session(lesson2, datetime.date(2015, 2, 2))

        response = self.client.get(self.get_url())

        self.assertQuerysetEqual(response.context["lesson_sessions"], [session1])

    def test_select_lessons_in_given_date(self):
        self.login(self.teacher)
        lesson2 = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.create_lesson_session(self.lesson)
        session2 = self.create_lesson_session(lesson2, datetime.date(2015, 2, 2))

        response = self.client.get(self.get_url(date="2015-02-02"))

        self.assertQuerysetEqual(response.context["lesson_sessions"], [session2])

    def test_context_contain_lesson_session_list(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertIn("lesson_sessions", response.context)

    def test_context_contains_given_date(self):
        self.login(self.teacher)
        date = "2021-01-01"
        response = self.client.get(self.get_url(date=date))

        self.assertIn("date", response.context)
        self.assertEqual(response.context["date"], date)

    def test_renders_links_to_lesson_session_detail_view(self):
        self.login(self.teacher)
        session = self.create_lesson_session(self.lesson)

        response = self.client.get(self.get_url())

        self.assertContains(
            response, reverse("lessons:session_detail", args=[session.pk])
        )

    def test_renders_appropriate_message_when_there_are_no_lessons_in_given_date(
        self,
    ):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertContains(response, "There are no lessons in the given date.")


class LessonSessionDetailViewTestCase(
    TeacherViewTestMixin,
    ResourceViewTestMixin,
    UsersMixin,
    ClassesMixin,
    LessonsMixin,
    TestCase,
):
    path_name = "lessons:session_detail"

    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_student(
            school_class=self.school_class,
            first_name="StudentFirstName",
            last_name="StudentLastName",
        )
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.lesson_session = self.create_lesson_session(self.lesson)

    def get_url(self, lesson_session_pk=None):
        lesson_session_pk = lesson_session_pk or self.lesson_session.pk

        return reverse(self.path_name, args=[lesson_session_pk])

    def get_nonexistent_resource_url(self):
        return self.get_url(lesson_session_pk=1234)

    @staticmethod
    def prepare_form_data(lesson_session, presences, topic, statuses):
        statuses_count = len(statuses)
        data = {
            "topic": topic,
            "presence_set-TOTAL_FORMS": statuses_count,
            "presence_set-INITIAL_FORMS": statuses_count,
        }

        for index, (presence, status) in enumerate(zip(presences, statuses)):
            data.update(
                {
                    f"presence_set-{index}-status": status,
                    f"presence_set-{index}-id": presence.pk,
                    f"presence_set-{index}-lesson_session": lesson_session.pk,
                }
            )

        return data

    def test_returns_403_when_user_is_not_a_teacher_of_desired_lesson_session(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.get(self.get_url())

        self.assertEqual(response.status_code, 403)

    def test_updates_lesson_session_and_presences(self):
        self.login(self.teacher)
        presences = self.create_presences(self.lesson_session, [self.student])
        expected_statuses = ["absent"]
        data = self.prepare_form_data(
            self.lesson_session, presences, "New topic", expected_statuses
        )

        self.client.post(self.get_url(), data=data)

        presences = Presence.objects.all()
        updated_statuses = [presence.status for presence in presences]
        self.assertEqual(updated_statuses, expected_statuses)

    def test_redirects_to_lesson_sessions_list_after_successful_update(self):
        self.login(self.teacher)
        presences = self.create_presences(self.lesson_session, [self.student])

        data = self.prepare_form_data(
            self.lesson_session, presences, "New Topic", ["absent"]
        )

        response = self.client.post(self.get_url(), data=data)

        self.assertRedirects(response, reverse("lessons:session_list"))

    def test_renders_success_message_after_successful_update(self):
        self.login(self.teacher)
        presences = self.create_presences(self.lesson_session, [self.student])
        data = self.prepare_form_data(
            self.lesson_session, presences, "New Topic", ["absent"]
        )

        response = self.client.post(self.get_url(), data=data, follow=True)

        self.assertContains(
            response, "The lesson session has been updated successfully."
        )

    def test_context_contain_form_and_formset(self):
        self.login(self.teacher)

        response = self.client.get(self.get_url())

        self.assertIn("lesson_session_form", response.context)
        self.assertIn("presences_formset", response.context)

    def test_renders_students_full_names_as_labels(self):
        self.login(self.teacher)
        self.create_presences(self.lesson_session, [self.student])

        response = self.client.get(self.get_url())

        self.assertContains(response, self.student.full_name)
