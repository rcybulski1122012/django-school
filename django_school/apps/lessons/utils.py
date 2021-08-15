from django_school.apps.lessons.models import LessonSession, Presence


def create_lesson_session(lesson):
    lesson_session = LessonSession.objects.create(lesson=lesson)

    presences = [
        Presence(student=student, lesson_session=lesson_session, status="none")
        for student in lesson.school_class.students.all()
    ]

    Presence.objects.bulk_create(presences)
