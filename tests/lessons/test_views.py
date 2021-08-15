import datetime

from django.test import TestCase
from django.urls import reverse

from django_school.apps.lessons.models import LESSONS_TIMES, WEEKDAYS
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
        user = self.create_user(username="not-a-teacher")

        response = self.client.get(reverse("lessons:teacher_timetable", args=[user.pk]))

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


class TeacherLessonsListView(
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
        self.assertRedirectsWhenNotLoggedIn(reverse("lessons:teacher_lessons"))

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        not_teacher = self.create_user(username="not-a-teacher")
        self.login(not_teacher)

        response = self.client.get(reverse("lessons:teacher_lessons"))

        self.assertEqual(response.status_code, 403)

    def test_context_contain_lessons_list(self):
        self.login(self.teacher)

        response = self.client.get(reverse("lessons:teacher_lessons"))

        self.assertIn("lessons", response.context)

    def test_selects_only_lessons_of_currently_logged_teacher(self):
        self.login(self.teacher)
        teacher2 = self.create_teacher(username="SecondTeacher2")
        lesson2 = self.create_lesson(self.subject, teacher2, self.school_class)
        exact1 = self.create_exact_lesson(self.lesson)
        self.create_exact_lesson(lesson2)

        response = self.client.get(reverse("lessons:teacher_lessons"))

        exact_lessons = response.context["lessons"]
        self.assertEqual(len(exact_lessons), 1)
        self.assertEqual(exact_lessons[0], exact1)

    def test_select_today_lessons_by_default(self):
        self.login(self.teacher)
        lesson2 = self.create_lesson(
            self.subject, self.teacher, self.school_class, weekday="mon"
        )
        exact1 = self.create_exact_lesson(self.lesson)
        self.create_exact_lesson(lesson2, datetime.date(2015, 2, 2))

        response = self.client.get(reverse("lessons:teacher_lessons"))

        exact_lessons = response.context["lessons"]
        self.assertEqual(len(exact_lessons), 1)
        self.assertEqual(exact_lessons[0], exact1)

    def test_select_lessons_in_given_date(self):
        self.login(self.teacher)
        lesson2 = self.create_lesson(self.subject, self.teacher, self.school_class)
        self.create_exact_lesson(self.lesson)
        exact2 = self.create_exact_lesson(lesson2, datetime.date(2015, 2, 2))

        response = self.client.get(
            f"{reverse('lessons:teacher_lessons')}?date=2015-02-02"
        )

        exact_lessons = response.context["lessons"]
        self.assertEqual(len(exact_lessons), 1)
        self.assertEqual(exact_lessons[0], exact2)

    def test_displays_appropriate_message_when_there_are_no_lessons_in_given_date(
        self,
    ):
        self.login(self.teacher)

        response = self.client.get(reverse("lessons:teacher_lessons"))

        self.assertContains(
            response, "There are no lessons in the given range of time."
        )

    # def test_performs_optimal_number_of_queries(self):
    #     self.login(self.teacher)
    #     ExactLesson(self.lesson)
    #
    #     with self.assertNumQueries(5):
    #         response = self.client.get(reverse("lessons:teacher_lessons"))
