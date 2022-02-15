from datetime import date

from django.core.management import BaseCommand

from django_school.apps.lessons.models import Lesson
from django_school.apps.lessons.utils import create_lesson_session


class Command(BaseCommand):
    help = "Creates LessonSession ans Attendance objects for lessons planned for today."

    def handle(self, *args, **kwargs):
        current_day = date.today().strftime("%a").lower()
        lessons = (
            Lesson.objects.filter(weekday=current_day)
            .select_related("school_class")
            .prefetch_related("school_class__students")
        )

        for lesson in lessons:
            create_lesson_session(lesson)
