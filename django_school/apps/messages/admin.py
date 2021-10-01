from django.contrib import admin
from martor.widgets import AdminMartorWidget

from django_school.apps.messages.models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    widgets = {"content": AdminMartorWidget}
