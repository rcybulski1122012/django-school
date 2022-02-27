from django_school.apps.users.models import Note


def unseen_notes_count(request):
    if not request.user.is_authenticated or request.user.is_teacher:
        return {}

    if request.user.is_parent:
        count = Note.objects.filter(
            student__parent=request.user, seen_by_parent=False
        ).count()
    else:
        count = Note.objects.filter(student=request.user, seen_by_student=False).count()

    return {"unseen_notes_count": count}
