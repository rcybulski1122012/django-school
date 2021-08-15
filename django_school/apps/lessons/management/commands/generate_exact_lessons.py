from datetime import date

from django.core.management import BaseCommand

from django_school.apps.lessons.models import Lesson
from django_school.apps.lessons.utils import generate_exact_lesson


class Command(BaseCommand):
    help = "Creates ExactLessons ans Presences objects for lessons planned for today."

    def handle(self, *args, **kwargs):
        current_day = date.today().strftime("%a").lower()
        lessons = (
            Lesson.objects.filter(weekday=current_day)
            .select_related("school_class")
            .prefetch_related("school_class__students")
        )

        for lesson in lessons:
            generate_exact_lesson(lesson)
