import datetime
import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.text import slugify

from django_school.apps.classes.models import Class
from django_school.apps.events.models import Event
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import (Attendance, Lesson,
                                               LessonSession, Subject)
from django_school.apps.lessons.utils import find_closest_future_date
from django_school.apps.users.models import ROLES

User = get_user_model()

CLASSES = [f"{number}{letter}" for number in "123" for letter in "abc"]
TEACHERS = [
    "Harmony Obrien",
    "Gregory Peters",
    "Jordan Mason",
    "Bill Shepard",
    "Helen Conner",
    "Alban Adams",
    "Louie Adams",
    "Alfie Garrett",
    "Polly Covington",
]
STUDENTS = [
    "Crispin Glisson",
    "Horace Weber",
    "Lonnie Aguilar",
    "Leopold Hudson",
    "Philippa Wood",
    "Cade Burke",
    "Rhea Mitchell",
    "Howard Schultz",
    "Harrison Fairbank",
    "Lois Smart",
    "Adele Harrison",
    "Hale Bradley",
    "Tyrone Parsons",
    "Willette Peay",
    "Gaylord Johnson",
]
SUBJECTS = [
    "Art",
    "Geography",
    "English",
    "Literacy",
    "Music",
    "Science",
    "Mathematics",
    "Chemistry",
    "Biology",
    "Physics",
    "Physical Education",
    "Information Technology",
]
GRADE_CATEGORIES = [
    "Exam 1",
    "Exam 2",
    "Exam 3",
    "Activity 1",
    "Activity 2",
    "Group project",
    "Final exam",
]
GLOBAL_EVENTS = [
    "Trip meeting",
    "School patron saint's day",
    "School party",
]
CLASS_EVENTS = [
    "Exam 1",
    "Interview",
    "Class trip",
    "Homework",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for f in [
            self.create_superuser,
            self.create_teachers,
            self.create_classes,
            self.create_students,
            self.create_subjects,
            self.create_loggable_teacher,
            self.create_loggable_student,
            self.create_lessons,
            self.create_grades_categories_and_grades,
            self.create_events,
        ]:
            try:
                f()
            except Exception as e:
                print(e)

    def create_superuser(self):
        self.create_loggable_user(
            username="admin",
            password="admin",
            first_name="Admin",
            last_name="Admin",
            is_superuser=True,
            is_staff=True,
        )

    def create_loggable_user(self, username, password, **kwargs):
        user, created = self.create_user(username=username, **kwargs)

        if created:
            user.set_password(password)
            user.save()

        return user, created

    @staticmethod
    def create_user(**kwargs):
        return User.objects.get_or_create(**kwargs)

    def create_loggable_teacher(self):
        self.create_loggable_user(
            username="teacher",
            password="teacher",
            role=ROLES.TEACHER,
            first_name="Lane",
            last_name="Erickson",
            gender="female",
            phone_number="123-456-789",
        )

    def create_loggable_student(self):
        school_class = Class.objects.first()

        self.create_loggable_user(
            username="student",
            password="student",
            role=ROLES.STUDENT,
            first_name="Clifford",
            last_name="Skinner",
            gender="male",
            phone_number="456-123-789",
            school_class=school_class,
        )

    @staticmethod
    def create_classes():
        teachers = list(User.teachers.all())
        classes = []

        for number in CLASSES:
            classes.append(Class(number=number, slug=number, tutor=teachers.pop()))

        Class.objects.bulk_create(classes)

    @staticmethod
    def create_teachers():
        teachers = []

        for full_name in TEACHERS:
            first_name, last_name = full_name.split()
            teachers.append(
                User(
                    role=ROLES.TEACHER,
                    first_name=first_name,
                    last_name=last_name,
                    slug=slugify(full_name),
                    username=full_name,
                )
            )

        User.objects.bulk_create(teachers)

    @staticmethod
    def create_students():
        classes = list(Class.objects.all())
        students = []
        for full_name in STUDENTS:
            first_name, last_name = full_name.split()
            students.append(
                User(
                    role=ROLES.STUDENT,
                    first_name=first_name,
                    last_name=last_name,
                    slug=slugify(full_name),
                    username=full_name,
                    school_class=random.choice(classes),
                )
            )

        User.objects.bulk_create(students)

    @staticmethod
    def create_subjects():
        subjects = [
            Subject(name=subject, slug=slugify(subject)) for subject in SUBJECTS
        ]

        Subject.objects.bulk_create(subjects)

    def create_lessons(self):
        classes = Class.objects.all()
        subjects = Subject.objects.all()
        teachers = list(User.teachers.all())
        lessons = []
        time_weekday_combinations = [
            (time[0], weekday[0])
            for time in Lesson.LESSONS_TIMES
            for weekday in Lesson.WEEKDAYS
        ]

        for school_class in classes:
            combinations = random.sample(time_weekday_combinations, len(subjects))
            for subject in subjects:
                if random.choice([True, False]):
                    time, weekday = combinations.pop()
                    lessons.append(
                        Lesson(
                            time=time,
                            weekday=weekday,
                            classroom=random.randint(1, 100),
                            subject=subject,
                            teacher=random.choice(teachers),
                            school_class=school_class,
                        )
                    )

        Lesson.objects.bulk_create(lessons)

        self.create_lesson_sessions_and_attendances(lessons)

    @staticmethod
    def create_lesson_sessions_and_attendances(lessons):
        lesson_sessions = []
        attendances = []
        for lesson in lessons:
            lesson_date = find_closest_future_date(lesson.weekday)
            lesson_session = LessonSession(lesson=lesson, date=lesson_date)
            lesson_sessions.append(lesson_session)
            status = random.choice(Attendance.ATTENDANCE_STATUSES[:-1])[0]
            attendances += [
                Attendance(
                    student=student, lesson_session=lesson_session, status=status
                )
                for student in lesson.school_class.students.all()
            ]

        LessonSession.objects.bulk_create(lesson_sessions)
        Attendance.objects.bulk_create(attendances)

    @staticmethod
    def create_grades_categories_and_grades():
        lessons = list(
            Lesson.objects.select_related("subject", "school_class", "teacher")
            .prefetch_related("school_class__students")
            .distinct("subject", "school_class")
        )
        categories = []

        for lesson in lessons:
            for grade_category in random.sample(GRADE_CATEGORIES, 4):
                category = GradeCategory(
                    school_class=lesson.school_class,
                    subject=lesson.subject,
                    name=grade_category,
                )
                category.teacher = (
                    lesson.teacher
                )  # not a model field, only to remember whose the lesson it is
                categories.append(category)

        GradeCategory.objects.bulk_create(categories)

        grades = []
        for category in categories:
            for student in category.school_class.students.all():
                grades.append(
                    Grade(
                        grade=random.choice(Grade.GRADES)[0],
                        weight=random.randint(1, 5),
                        category=category,
                        subject=category.subject,
                        student=student,
                        teacher=category.teacher,
                    )
                )

        Grade.objects.bulk_create(grades)

    @staticmethod
    def create_events():
        teacher = User.teachers.get(username="teacher")
        classes = Class.objects.all()
        today = datetime.datetime.today()
        events = []

        for event in GLOBAL_EVENTS:
            events.append(
                Event(
                    title=event,
                    description=event,
                    date=today + datetime.timedelta(days=random.randint(-30, 30)),
                    teacher=teacher,
                )
            )

        for school_class in classes:
            for event in random.sample(CLASS_EVENTS, 3):
                events.append(
                    Event(
                        title=event,
                        description=event,
                        date=today + datetime.timedelta(days=random.randint(-30, 30)),
                        teacher=teacher,
                        school_class=school_class,
                    )
                )

        Event.objects.bulk_create(events)
