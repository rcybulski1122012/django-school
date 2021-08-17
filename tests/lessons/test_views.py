import datetime

from django.test import TestCase
from django.urls import reverse

from django_school.apps.lessons.models import LESSONS_TIMES, WEEKDAYS, Presence
from django_school.apps.lessons.views import SUCCESS_LESSON_SESSION_UPDATE_MESSAGE
from tests.utils import ClassesMixin, CommonMixin, LessonsMixin, UsersMixin


class TestTimetableView(ClassesMixin, UsersMixin, LessonsMixin, CommonMixin, TestCase):
    def test_returns_404_when_class_does_not_exits(self):
        response = self.client.get(reverse("lessons:class_timetable", args=[100]))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_school_class(self):
        school_class = self.create_class()

        response = self.client.get(
            reverse("lessons:class_timetable", args=[school_class.pk])
        )

        self.assertEqual(response.context["school_class"], school_class)

    def test_context_contains_weekdays_and_lessons_times(self):
        school_class = self.create_class()

        response = self.client.get(
            reverse("lessons:class_timetable", args=[school_class.pk])
        )

        self.assertEqual(response.context["weekdays"], WEEKDAYS)
        self.assertEqual(response.context["lessons_times"], LESSONS_TIMES)

    def test_renders_lessons(self):
        teacher = self.create_teacher()
        subject = self.create_subject()
        school_class = self.create_class()
        lesson = self.create_lesson(subject, teacher, school_class)

        response = self.client.get(
            reverse("lessons:class_timetable", args=[school_class.pk])
        )

        self.assertContainsFew(
            response,
            teacher.full_name,
            subject.name,
            school_class.number,
            lesson.classroom,
        )

    def test_performs_optimal_number_of_queries(self):
        teacher = self.create_teacher()
        subject = self.create_subject()
        school_class = self.create_class()
        [
            self.create_lesson(subject, teacher, school_class, time=time)
            for time in LESSONS_TIMES
        ]

        with self.assertNumQueries(4):
            self.client.get(reverse("lessons:class_timetable", args=[school_class.pk]))


class TestTeacherTimetableView(
    ClassesMixin, UsersMixin, LessonsMixin, CommonMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.subject = self.create_subject()
        self.school_class = self.create_class()

    def test_returns_404_when_user_is_not_a_teacher(self):
        not_teacher = self.create_user(username="not-a-teacher")

        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[not_teacher.pk])
        )

        self.assertEqual(response.status_code, 404)

    def test_context_contains_teacher(self):
        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[self.teacher.pk])
        )

        self.assertEqual(response.context["teacher"], self.teacher)

    def test_context_contains_weekdays_and_lessons_times(self):
        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[self.teacher.pk])
        )

        self.assertEqual(response.context["weekdays"], WEEKDAYS)
        self.assertEqual(response.context["lessons_times"], LESSONS_TIMES)

    def test_renders_lessons(self):
        lesson = self.create_lesson(self.subject, self.teacher, self.school_class)

        response = self.client.get(
            reverse("lessons:teacher_timetable", args=[self.teacher.pk])
        )

        self.assertContainsFew(
            response,
            self.teacher.full_name,
            self.subject.name,
            lesson.classroom,
        )


class TestTimetableListView(ClassesMixin, UsersMixin, TestCase):
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


class TestTeacherLessonsListView(
    UsersMixin, CommonMixin, LessonsMixin, ClassesMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
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
        not_teacher = self.create_user(username="not-a-teacher")
        self.login(not_teacher)

        response = self.client.get(reverse("lessons:sessions"))

        self.assertEqual(response.status_code, 403)

    def test_context_contain_lesson_session_list(self):
        self.login(self.teacher)

        response = self.client.get(reverse("lessons:sessions"))

        self.assertIn("lesson_sessions", response.context)

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

    def test_performs_optimal_number_of_queries(self):
        self.login(self.teacher)
        [self.create_lesson_session(self.lesson) for _ in range(5)]

        with self.assertNumQueries(6):
            self.client.get(reverse("lessons:sessions"))


class TestLessonSessionDetailView(UsersMixin, LessonsMixin, ClassesMixin, TestCase):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
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
        not_teacher = self.create_user(username="not-a-teacher")
        self.login(not_teacher)

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

        self.assertIn("form", response.context)
        self.assertIn("formset", response.context)

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
        student = self.create_user("student123", school_class=self.school_class)
        presences = self.create_presences(self.lesson_session, [student])

        data = self._prepare_form_data(
            self.lesson_session, presences, "New Topic", ["absent"]
        )
        response = self.client.post(
            reverse("lessons:session_detail", args=[self.lesson_session.pk]), data=data
        )

        self.assertRedirects(response, reverse("lessons:sessions"))

    def test_displays_success_message_after_successful_update(self):
        self.login(self.teacher)
        student = self.create_user("student123", school_class=self.school_class)
        presences = self.create_presences(self.lesson_session, [student])

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
        student = self.create_user(
            "student123",
            school_class=self.school_class,
            first_name="StudentFirstName",
            last_name="StudentLastName",
        )
        presences = self.create_presences(self.lesson_session, [student])
        response = self.client.get(
            reverse("lessons:session_detail", args=[self.lesson_session.pk]),
        )

        self.assertContains(response, student.full_name)
