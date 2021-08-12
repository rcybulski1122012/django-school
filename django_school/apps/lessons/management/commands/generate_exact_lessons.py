from datetime import date

from django.core.management import BaseCommand

from django_school.apps.lessons.models import ExactLesson, Lesson, Presence


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
            exact_lesson = ExactLesson.objects.create(lesson=lesson)

            presences = [
                Presence(student=student, exact_lesson=exact_lesson, status="none")
                for student in lesson.school_class.students.all()
            ]

            Presence.objects.bulk_create(presences)
