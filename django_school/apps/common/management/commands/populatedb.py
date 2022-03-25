import datetime
import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.utils.text import slugify

from django_school.apps.classes.models import Class
from django_school.apps.events.models import Event, EventStatus
from django_school.apps.grades.models import Grade, GradeCategory
from django_school.apps.lessons.models import (Attendance, Lesson,
                                               LessonSession, Subject)
from django_school.apps.lessons.utils import find_closest_future_date
from django_school.apps.users.models import ROLES

User = get_user_model()


TEACHERS = [
    "Alastor Moody",
    "Aurora Sinistra",
    "Bathsheda Babbling",
    "Charity Burbage",
    "Dolores Umbridge",
    "Filius Flitwick",
    "Gilderoy Lockhart",
    "Horace Slughorn",
    "Minerva McGonagall",
    "Pomona Sprout",
    "Quirinus Quirrell",
    "Remus Lupin",
    "Rolanda Hooch",
    "Rubeus Hagrid",
    "Severus Snape",
]

SUBJECT_TEACHERS_DICT = {
    "Transfiguration": ["Albus Dumbledore", "Minerva McGonagall"],
    "Defence Against the Dark Arts": [
        "Alastor Moody",
        "Dolores Umbridge",
        "Gilderoy Lockhart",
        "Quirinus Quirrell",
        "Remus Lupin",
        "Severus Snape",
    ],
    "Astronomy": ["Aurora Sinistra"],
    "Ancient Runes": ["Bathsheda Babbling"],
    "Muggle Studies": ["Quirinus Quirrell", "Charity Burbage"],
    "Charms": ["Filius Flitwick"],
    "Potions": ["Horace Slughorn", "Severus Snape"],
    "Flying": ["Rolanda Hooch"],
    "Herbology": ["Pomona Sprout"],
    "Care of Magical Creatures": ["Rubeus Hagrid"],
}

STUDENT_PARENT_CLASS_LISTS = [
    ["Harry Potter", None, "Gryffindor"],
    ["Hermione Granger", None, "Gryffindor"],
    ["Seamus Finnigan", "Mr. Finnigan", "Gryffindor"],
    ["Dean Thomas", "Mrs. Thomas", "Gryffindor"],
    ["Ginny Weasley", "Arthur Weasley", "Gryffindor"],
    ["Lavender Brown", None, "Gryffindor"],
    ["Neville Longbottom", "Augusta Longbottom", "Gryffindor"],
    ["Draco Malfoy", "Lucius Malfoy", "Slytherin"],
    ["Vincent Crabbe", "Crabbe Senior", "Slytherin"],
    ["Gregory Goyle", "Goyle Senior", "Slytherin"],
    ["Millicent Bulstrode", "Violetta Bulstrode", "Slytherin"],
    ["Pansy Parkinson", "Perseus Parkinson", "Slytherin"],
    ["Blaise Zabini", "Mrs Zabini", "Slytherin"],
    ["Roger Davies", "Mr. Davies", "Ravenclaw"],
    ["Cho Chang", "Madam Chang", "Ravenclaw"],
    ["Padma Patil", "Mr. Patil", "Ravenclaw"],
    ["Luna Lovegood", "Xenophilius Lovegood", "Ravenclaw"],
    ["Marcus Belby", "Damocles Belby", "Ravenclaw"],
    ["Ernie Macmillan", "George Macmillan", "Hufflepuff"],
    ["Susan Bones", "Edgar Bones", "Hufflepuff"],
    ["Justin Finch-Fletchley", None, "Hufflepuff"],
    ["Cedric Diggory", "Amos Diggory", "Hufflepuff"],
]


SUBJECTS = [
    "Transfiguration",
    "Defence Against the Dark Arts",
    "Astronomy",
    "Ancient Runes",
    "Muggle Studies",
    "Charms",
    "Divination",
    "Potions",
    "Herbology",
    "Flying",
    "Care of Magical Creatures",
]


CLASSES = [
    "Gryffindor",
    "Slytherin",
    "Ravenclaw",
    "Hufflepuff",
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
    "Quidditch Tournament",
    "Triwizard tournament" "School party",
]


CLASS_EVENTS = [
    "Exam 1",
    "Exam 2",
    "Exam 3",
    "Homework",
    "Group project",
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for f in [
            self.create_superuser,  # ok
            self.create_teachers,  # ok
            self.create_classes,  # ok
            self.create_students_and_parents,  # ok
            self.create_subjects,  # ok
            self.create_loggable_teacher,  # ok
            self.create_loggable_student,  # ok
            self.create_loggable_parent,  # ok
            self.create_lessons,
            self.create_grades_categories_and_grades,  # ok
            self.create_events,  # ok
        ]:
            try:
                f()
            except Exception as e:
                import traceback

                traceback.print_exc()
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
        self.school_class = Class.objects.first()

        self.teacher, _ = self.create_loggable_user(
            username="teacher",
            password="teacher",
            role=ROLES.TEACHER,
            first_name="Albus",
            last_name="Dumbledore",
            gender="male",
            phone_number="123-456-789",
        )

        self.school_class.tutor = self.teacher
        self.school_class.save()

    def create_loggable_student(self):
        self.create_loggable_user(
            username="student",
            password="student",
            role=ROLES.STUDENT,
            first_name="Ron",
            last_name="Weasley",
            gender="male",
            phone_number="456-123-789",
            school_class=self.school_class,
        )

    def create_loggable_parent(self):
        child = User.students.get(username="student")

        self.create_loggable_user(
            username="parent",
            password="parent",
            role=ROLES.PARENT,
            first_name="Molly",
            last_name="Weasley",
            gender="female",
            phone_number="789-456-123",
            child=child,
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
    def create_students_and_parents():
        classes = {
            class_name: Class.objects.get(number=class_name) for class_name in CLASSES
        }

        students = []
        for student_name, _, class_name in STUDENT_PARENT_CLASS_LISTS:
            first_name, last_name = student_name.split()
            students.append(
                User(
                    role=ROLES.STUDENT,
                    first_name=first_name,
                    last_name=last_name,
                    slug=slugify(student_name),
                    username=student_name,
                    school_class=classes[class_name],
                )
            )

        User.objects.bulk_create(students)

        parents = []
        for student, (_, parent_name, _) in zip(students, STUDENT_PARENT_CLASS_LISTS):
            if parent_name is None:
                continue

            first_name, last_name = parent_name.split()
            parents.append(
                User(
                    role=ROLES.STUDENT,
                    first_name=first_name,
                    last_name=last_name,
                    slug=slugify(parent_name),
                    username=parent_name,
                    child=student,
                )
            )

        User.objects.bulk_create(parents)

    @staticmethod
    def create_subjects():
        subjects = [
            Subject(name=subject, slug=slugify(subject)) for subject in SUBJECTS
        ]

        Subject.objects.bulk_create(subjects)

    def create_lessons(self):
        classes = Class.objects.all()
        subjects = {subject.name: subject for subject in Subject.objects.all()}
        teachers_dict = {teacher.full_name: teacher for teacher in User.teachers.all()}
        for full_name in TEACHERS:
            first_name, last_name = full_name.split()
            teachers_dict[full_name] = User.teachers.get(
                first_name=first_name, last_name=last_name
            )
        lessons = []
        time_weekday_combinations = [
            (time[0], weekday[0])
            for time in Lesson.LESSONS_TIMES
            for weekday in Lesson.WEEKDAYS
        ]

        for school_class in classes:
            combinations = random.sample(time_weekday_combinations, len(subjects) * 5)
            for subject, teachers in SUBJECT_TEACHERS_DICT.items():
                for _ in range(3):
                    time, weekday = combinations.pop()
                    teacher = teachers_dict[random.choice(teachers)]
                    lessons.append(
                        Lesson(
                            time=time,
                            weekday=weekday,
                            classroom=random.randint(1, 100),
                            subject=subjects[subject],
                            teacher=teacher,
                            school_class=school_class,
                        )
                    )

        # to ensure that the loggable teacher is teaching the loggable student
        lessons.append(
            Lesson(
                time=Lesson.LESSONS_TIMES[0][0],
                weekday=Lesson.WEEKDAYS[0][0],
                classroom=1,
                subject=Subject.objects.first(),
                teacher=self.teacher,
                school_class=self.school_class,
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

        for event in events:
            EventStatus.objects.create_multiple(event)
