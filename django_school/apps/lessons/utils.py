import datetime

from django_school.apps.lessons.models import Attendance, LessonSession


def create_lesson_session(lesson, date=None):
    lesson_session = LessonSession.objects.create(lesson=lesson, date=date)

    attendances = [
        Attendance(student=student, lesson_session=lesson_session, status="none")
        for student in lesson.school_class.students.all()
    ]

    Attendance.objects.bulk_create(attendances)


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
