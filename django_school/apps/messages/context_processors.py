from django_school.apps.messages.models import MessageStatus


def unread_messages_count(request):
    if not request.user.is_authenticated:
        return {"unread_messages_count": 0}

    count = MessageStatus.objects.filter(receiver=request.user, is_read=False).count()
    return {"unread_messages_count": count}
