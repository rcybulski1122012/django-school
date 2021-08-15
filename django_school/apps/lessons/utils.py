from django_school.apps.lessons.models import ExactLesson, Presence


def generate_exact_lesson(lesson):
    exact_lesson = ExactLesson.objects.create(lesson=lesson)

    presences = [
        Presence(student=student, exact_lesson=exact_lesson, status="none")
        for student in lesson.school_class.students.all()
    ]

    Presence.objects.bulk_create(presences)
