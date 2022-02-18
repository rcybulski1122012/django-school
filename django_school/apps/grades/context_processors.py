from django_school.apps.grades.models import Grade


def unseen_grades_count(request):
    if not request.user.is_authenticated or request.user.is_teacher:
        return {}

    if request.user.is_parent:
        count = Grade.objects.filter(
            student__parent=request.user, seen_by_parent=False
        ).count()
    else:
        count = Grade.objects.filter(
            student=request.user, seen_by_student=False
        ).count()

    return {"unseen_grades_count": count}
