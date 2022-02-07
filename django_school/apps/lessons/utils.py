import datetime

from django_school.apps.lessons.models import LessonSession, Presence


def create_lesson_session(lesson, date=None):
    lesson_session = LessonSession.objects.create(lesson=lesson, date=date)

    presences = [
        Presence(student=student, lesson_session=lesson_session, status="none")
        for student in lesson.school_class.students.all()
    ]

    Presence.objects.bulk_create(presences)


def find_closest_future_date(weekday):
    weekday_number = {
        "mon": 0,
        "tue": 1,
        "wed": 2,
        "thu": 3,
        "fri": 4,
        "sat": 5,
        "sun": 6,
    }[weekday]
    today = datetime.datetime.today()

    delta = (weekday_number - today.weekday()) % 7
    return today + datetime.timedelta(days=delta)
