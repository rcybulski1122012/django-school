import datetime

from django.test import TestCase
from django.urls import reverse

from django_school.apps.lessons.models import Lesson, Presence
from django_school.apps.lessons.views import SUCCESS_LESSON_SESSION_UPDATE_MESSAGE
from tests.utils import ClassesMixin, CommonMixin, LessonsMixin, UsersMixin


class TestClassTimetableView(
    UsersMixin, ClassesMixin, LessonsMixin, CommonMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.subject = self.create_subject()
        self.school_class = self.create_class()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)

    def test_returns_404_when_class_does_not_exits(self):
        response = self.client.get(reverse("lessons:class_timetable", args=["slug"]))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_school_class(self):
        response = self.client.get(
            reverse("lessons:class_timetable", args=[self.school_class.slug])
        )

        self.assertEqual(response.context["school_class"], self.school_class)

    def test_context_contains_weekdays_and_lessons_times(self):
        response = self.client.get(
            reverse("lessons:class_timetable", args=[self.school_class.slug])
        )

        self.assertEqual(response.context["weekdays"], Lesson.WEEKDAYS)
        self.assertEqual(response.context["lessons_times"], Lesson.LESSONS_TIMES)

    def test_renders_lessons(self):
        response = self.client.get(
            reverse("lessons:class_timetable", args=[self.school_class.slug])
        )

        self.assertContainsFew(
            response,
            self.teacher.full_name,
            self.subject.name,
            self.school_class.number,
            self.lesson.classroom,
        )


class TestTeacherTimetableView(
    UsersMixin, ClassesMixin, LessonsMixin, CommonMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.student = self.create_user(username="student123")
        self.subject = self.create_subject()
        self.school_class = self.create_class()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)

    def test_returns_404_when_user_is_not_a_teacher(self):
        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[self.student.slug])
        )

        self.assertEqual(response.status_code, 404)

    def test_context_contains_weekdays_and_lessons_times(self):
        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[self.teacher.slug])
        )

        self.assertEqual(response.context["weekdays"], Lesson.WEEKDAYS)
        self.assertEqual(response.context["lessons_times"], Lesson.LESSONS_TIMES)

    def test_context_contains_teacher(self):
        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[self.teacher.slug])
        )

        self.assertEqual(response.context["teacher"], self.teacher)

    def test_renders_lessons(self):
        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[self.teacher.slug])
        )

        self.assertContainsFew(
            response,
            self.teacher.full_name,
            self.subject.name,
            self.lesson.classroom,
        )


class TestTimetablesListView(UsersMixin, ClassesMixin, CommonMixin, TestCase):
    def test_context_contains_lists_of_classes_and_teachers(self):
        school_classes = [self.create_class(number=number) for number in "1234"]
        teachers = [
            self.create_teacher(
                username=f"teacher-nr-{number}", first_name=f"teacher-nr-{number}"
            )
            for number in "1234"
        ]

        response = self.client.get(reverse("lessons:timetables_list"))

        self.assertQuerysetEqual(response.context["school_classes"], school_classes)
        self.assertQuerysetEqual(response.context["teachers"], teachers)

    def test_renders_links_to_timetables(self):
        school_class = self.create_class()
        teacher = self.create_teacher()

        response = self.client.get(reverse("lessons:timetables_list"))

        self.assertContainsFew(
            response,
            reverse("lessons:class_timetable", args=[school_class.slug]),
            reverse("lessons:teacher_timetable", args=[teacher.slug]),
        )


class TestTeacherLessonsListView(
    UsersMixin, ClassesMixin, LessonsMixin, CommonMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="student123", school_class=self.school_class
        )
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(
            self.subject,
            self.teacher,
            self.school_class,
            weekday="fri",
        )

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(reverse("lessons:sessions"))

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.login(self.student)

        response = self.client.get(reverse("lessons:sessions"))

        self.assertEqual(response.status_code, 403)

    def test_returns_200_when_user_is_in_teachers_group(self):
        self.login(self.teacher)

        response = self.client.get(reverse("lessons:sessions"))

        self.assertEqual(response.status_code, 200)

    def test_context_contain_lesson_session_list(self):
        self.login(self.teacher)

        response = self.client.get(reverse("lessons:sessions"))

        self.assertIn("lesson_sessions", response.context)

    def test_context_contains_given_date(self):
        self.login(self.teacher)
        url = f'{reverse("lessons:sessions")}?date=2021-01-01'

        response = self.client.get(url)

        self.assertIn("date", response.context)
        self.assertEqual(response.context["date"], "2021-01-01")

    def test_renders_links_to_lesson_session_detail_view(self):
        self.login(self.teacher)
        session = self.create_lesson_session(self.lesson)

        response = self.client.get(reverse("lessons:sessions"))

        self.assertContains(
            response, reverse("lessons:session_detail", args=[session.pk])
        )

    def test_selects_only_lesson_sessions_of_currently_logged_teacher(self):
        self.login(self.teacher)
        teacher2 = self.create_teacher(username="SecondTeacher2")
        lesson2 = self.create_lesson(self.subject, teacher2, self.school_class)
        session1 = self.create_lesson_session(self.lesson)
        self.create_lesson_session(lesson2)

        response = self.client.get(reverse("lessons:sessions"))

        sessions = response.context["lesson_sessions"]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], session1)

    def test_select_today_lesson_sessions_by_default(self):
        self.login(self.teacher)
        lesson2 = self.create_lesson(
            self.subject, self.teacher, self.school_class, weekday="mon"
        )
        session1 = self.create_lesson_session(self.lesson)
        self.create_lesson_session(lesson2, datetime.date(2015, 2, 2))

        response = self.client.get(reverse("lessons:sessions"))

        sessions = response.context["lesson_sessions"]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], session1)

    def test_select_lessons_in_given_date(self):
        self.login(self.teacher)
        lesson2 = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.create_lesson_session(self.lesson)
        session2 = self.create_lesson_session(lesson2, datetime.date(2015, 2, 2))

        response = self.client.get(f"{reverse('lessons:sessions')}?date=2015-02-02")

        sessions = response.context["lesson_sessions"]
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0], session2)

    def test_displays_appropriate_message_when_there_are_no_lessons_in_given_date(
        self,
    ):
        self.login(self.teacher)

        response = self.client.get(reverse("lessons:sessions"))

        self.assertContains(
            response, "There are no lessons in the given range of time."
        )


class TestLessonSessionDetailView(UsersMixin, ClassesMixin, LessonsMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="student123",
            school_class=self.school_class,
            first_name="StudentFirstName",
            last_name="StudentLastName",
        )
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.lesson_session = self.create_lesson_session(self.lesson)

    @staticmethod
    def _prepare_form_data(lesson_session, presences, topic, statuses):
        statuses_count = len(statuses)
        data = {
            "topic": topic,
            "presence_set-TOTAL_FORMS": statuses_count,
            "presence_set-INITIAL_FORMS": statuses_count,
        }

        for index, presence, status in zip(range(statuses_count), presences, statuses):
            data.update(
                {
                    f"presence_set-{index}-status": status,
                    f"presence_set-{index}-id": presence.id,
                    f"presence_set-{index}-lesson_session": lesson_session.id,
                }
            )

        return data

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(
            reverse("lessons:session_detail", args=[self.lesson_session.pk])
        )

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.login(self.student)

        response = self.client.get(
            reverse("lessons:session_detail", args=[self.lesson_session.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_returns_200_when_user_is_in_teachers_group(self):
        self.login(self.teacher)

        response = self.client.get(
            reverse("lessons:session_detail", args=[self.lesson_session.pk])
        )

        self.assertEqual(response.status_code, 200)

    def test_returns_403_when_user_is_not_a_teacher_of_desired_lesson_session(self):
        teacher2 = self.create_teacher(username="teacher2")
        self.login(teacher2)

        response = self.client.get(
            reverse("lessons:session_detail", args=[self.lesson_session.pk])
        )

        self.assertEqual(response.status_code, 403)

    def test_returns_404_when_lesson_session_does_not_exist(self):
        self.login(self.teacher)

        response = self.client.get(reverse("lessons:session_detail", args=[100]))

        self.assertEqual(response.status_code, 404)

    def test_context_contain_form_and_formset(self):
        self.login(self.teacher)

        response = self.client.get(
            reverse("lessons:session_detail", args=[self.lesson_session.pk])
        )

        self.assertIn("lesson_session_form", response.context)
        self.assertIn("presences_formset", response.context)

    def test_updates_lesson_session_and_presences_when_everything_is_OK(self):
        self.login(self.teacher)
        students = [
            self.create_user(f"student{i}", school_class=self.school_class)
            for i in range(5)
        ]
        presences = self.create_presences(self.lesson_session, students)
        expected_statuses = ["absent"] * 5
        data = self._prepare_form_data(
            self.lesson_session, presences, "New topic", expected_statuses
        )

        self.client.post(
            reverse("lessons:session_detail", args=[self.lesson_session.pk]), data=data
        )

        presences = Presence.objects.all()
        updated_statuses = [presence.status for presence in presences]
        self.assertEqual(updated_statuses, expected_statuses)

    def test_redirects_to_lesson_sessions_list_after_successful_update(self):
        self.login(self.teacher)
        presences = self.create_presences(self.lesson_session, [self.student])

        data = self._prepare_form_data(
            self.lesson_session, presences, "New Topic", ["absent"]
        )

        response = self.client.post(
            reverse("lessons:session_detail", args=[self.lesson_session.pk]), data=data
        )

        self.assertRedirects(response, reverse("lessons:sessions"))

    def test_displays_success_message_after_successful_update(self):
        self.login(self.teacher)
        presences = self.create_presences(self.lesson_session, [self.student])
        data = self._prepare_form_data(
            self.lesson_session, presences, "New Topic", ["absent"]
        )

        response = self.client.post(
            reverse("lessons:session_detail", args=[self.lesson_session.pk]),
            data=data,
            follow=True,
        )

        self.assertContains(response, SUCCESS_LESSON_SESSION_UPDATE_MESSAGE)

    def test_displays_students_full_names_as_labels(self):
        self.login(self.teacher)
        self.create_presences(self.lesson_session, [self.student])

        response = self.client.get(
            reverse("lessons:session_detail", args=[self.lesson_session.pk]),
        )

        self.assertContains(response, self.student.full_name)
