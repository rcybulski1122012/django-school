from django import forms

from django_school.apps.messages.models import Message, MessageStatus


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ["topic", "content", "receivers"]

    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop("sender")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        message = super().save(commit=False)
        message.sender = self.sender

        if commit:
            message.save()
            MessageStatus.objects.create_multiple(
                message, self.cleaned_data["receivers"]
            )

        return message
