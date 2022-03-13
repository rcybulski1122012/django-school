from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import SetPasswordForm, UserCreationForm

from django_school.apps.users.models import Note

User = get_user_model()


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ["note", "student"]

    def __init__(self, *args, **kwargs):
        self.teacher = kwargs.pop("teacher")

        super().__init__(*args, **kwargs)

        self.fields["student"].queryset = User.students.visible_to_user(self.teacher)

    def is_valid(self):
        self.instance.teacher = self.teacher

        return super().is_valid()


class UserCreationWithoutPasswordForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].required = False
        self.fields["password2"].required = False


class SetPasswordWithActivationForm(SetPasswordForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.is_active = True

        if commit:
            user.save()

        return user
