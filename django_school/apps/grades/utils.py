from django_school.apps.lessons.models import Lesson


def does_the_teacher_teach_the_subject_to_the_class(teacher, subject, school_class):
    return Lesson.objects.filter(
        school_class=school_class,
        subject=subject,
        teacher=teacher,
    ).exists()
