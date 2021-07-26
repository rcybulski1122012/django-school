from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

from django_school.apps.classes.models import Class

User = get_user_model()


class AccountsMixin:
    DEFAULT_USERNAME = "username"
    DEFAULT_PASSWORD = "password"

    @staticmethod
    def create_user(username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
        return User.objects.create_user(username=username, password=password)

    def login(self, username=DEFAULT_USERNAME, password=DEFAULT_PASSWORD):
        self.client.login(username=username, password=password)

    def logout(self):
        self.client.logout()

    @staticmethod
    def add_user_to_group(user, group_name):
        group = Group.objects.get(name=group_name)
        user.groups.add(group)


class ClassesMixin:
    DEFAULT_NUMBER = "1a"

    @staticmethod
    def create_class(number=DEFAULT_NUMBER, tutor=None):
        return Class.objects.create(number=number, tutor=tutor)
