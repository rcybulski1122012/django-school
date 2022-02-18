from django_school.apps.events.models import EventStatus


def unseen_events_count(request):
    if not request.user.is_authenticated:
        return {}

    count = EventStatus.objects.filter(user=request.user, seen=False).count()
    return {"unseen_events_count": count}
