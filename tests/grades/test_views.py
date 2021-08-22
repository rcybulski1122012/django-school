from django.test import TestCase
from django.urls import reverse

from django_school.apps.grades.models import Grade
from django_school.apps.grades.views import SUCCESS_GRADE_CREATE_MESSAGE
from tests.utils import ClassesMixin, CommonMixin, LessonsMixin, UsersMixin


class TestGradeCreateView(
    UsersMixin, ClassesMixin, LessonsMixin, CommonMixin, TestCase
):
    def setUp(self):
        self.teacher = self.create_teacher()
        self.school_class = self.create_class()
        self.student = self.create_user(
            username="student123", school_class=self.school_class
        )
        self.subject = self.create_subject()
        self.lesson = self.create_lesson(self.subject, self.teacher, self.school_class)

    def _get_example_form_data(self):
        return {
            "grade": 5.00,
            "weight": 1,
            "comment": "Math Exam",
            "subject": self.subject.pk,
            "student": self.student.pk,
        }

    def test_redirects_when_user_is_not_logged_in(self):
        self.assertRedirectsWhenNotLoggedIn(
            reverse("grades:add", args=[self.school_class.slug])
        )

    def test_returns_403_when_user_is_not_in_teachers_group(self):
        self.login(self.student)

        response = self.client.get(reverse("grades:add", args=[self.school_class.slug]))

        self.assertEqual(response.status_code, 403)

    def test_returns_200_when_user_is_in_teachers_group(self):
        self.login(self.teacher)

        response = self.client.get(reverse("grades:add", args=[self.school_class.slug]))

        self.assertEqual(response.status_code, 200)

    def test_return_403_when_the_teacher_is_not_teaching_the_class(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="2c")

        response = self.client.get(reverse("grades:add", args=[school_class2.slug]))

        self.assertEqual(response.status_code, 403)

    def test_returns_404_when_class_with_given_number_does_not_exist(self):
        self.login(self.teacher)

        response = self.client.get(reverse("grades:add", args=["123c"]))

        self.assertEqual(response.status_code, 404)

    def test_context_contains_class_number(self):
        self.login(self.teacher)

        response = self.client.get(reverse("grades:add", args=[self.school_class.slug]))

        self.assertIn("slug", response.context)

    # form subject queryset should contains given class learning subjects
    # which are taught by the currently logged teacher
    def test_form_subject_queryset(self):
        self.login(self.teacher)

        # other class subject
        subject2 = self.create_subject(name="subject2")
        school_class2 = self.create_class(number="class2")
        self.create_user(username="student2", school_class=school_class2)
        self.create_lesson(subject2, self.teacher, school_class2)

        # other teacher subject
        teacher2 = self.create_teacher(username="teacher2")
        subject3 = self.create_subject(name="subject3")
        self.create_lesson(subject3, teacher2, self.school_class)

        response = self.client.get(reverse("grades:add", args=[self.school_class.slug]))

        subject_qs = response.context["form"].fields["subject"].queryset
        self.assertQuerysetEqual(subject_qs, [self.subject])

    def test_form_student_queryset(self):
        self.login(self.teacher)
        school_class2 = self.create_class(number="class2")
        self.create_user(username="student2", school_class=school_class2)

        response = self.client.get(reverse("grades:add", args=[self.school_class.slug]))

        students_qs = response.context["form"].fields["student"].queryset
        self.assertQuerysetEqual(students_qs, [self.student])

    def test_creates_grade(self):
        self.login(self.teacher)
        data = self._get_example_form_data()

        self.client.post(reverse("grades:add", args=[self.school_class.slug]), data)

        self.assertTrue(Grade.objects.exists())

    def test_redirect_after_successful_grade_adding(self):
        self.login(self.teacher)
        data = self._get_example_form_data()

        response = self.client.post(
            reverse("grades:add", args=[self.school_class.slug]), data
        )

        self.assertRedirects(response, reverse("classes:list"))

    def test_displays_success_message_after_successful_create(self):
        self.login(self.teacher)
        data = self._get_example_form_data()

        response = self.client.post(
            reverse("grades:add", args=[self.school_class.slug]), data, follow=True
        )

        self.assertContains(response, SUCCESS_GRADE_CREATE_MESSAGE)

    def test_set_initial_data_to_form_if_given(self):
        self.login(self.teacher)
        url = (
            f'{reverse("grades:add", args=[self.school_class.slug])}'
            f"?subject={self.subject.pk}&student={self.student.pk}"
        )

        response = self.client.get(url)

        form = response.context["form"]
        expected = {"student": f"{self.student.pk}", "subject": f"{self.subject.pk}"}
        self.assertEqual(form.initial, expected)
