from datetime import date

from django.core.management import BaseCommand

from django_school.apps.lessons.models import ExactLesson, Lesson


class Command(BaseCommand):
    help = "Creates ExactLessons objects for lessons planned for today."

    def handle(self, *args, **kwargs):
        current_day = date.today().strftime("%a").lower()
        lessons = Lesson.objects.filter(weekday=current_day)

        for lesson in lessons:
            ExactLesson.objects.create(lesson=lesson)
