from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.contrib.messages.views import SuccessMessageMixin
from django.http import Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from django_school.apps.common.utils import (AjaxRequiredMixin,
                                             RolesRequiredMixin)
from django_school.apps.users.forms import NoteForm
from django_school.apps.users.models import ROLES, Note

User = get_user_model()


class StudentDetailView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.TEACHER), DetailView
):
    model = User
    slug_url_kwarg = "student_slug"
    template_name = "users/student_detail.html"
    context_object_name = "student"

    def dispatch(self, request, *args, **kwargs):
        if self.is_requested_user_role_is_teacher():
            raise Http404()

        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            User.students.visible_to_user(self.request.user)
            .with_teacher_notes(self.request.user)
            .select_related("address", "school_class__tutor")
        )

    def is_requested_user_role_is_teacher(self):
        return User.objects.filter(
            slug=self.kwargs[self.slug_url_kwarg], role=ROLES.TEACHER
        ).exists()


class PasswordChangeWithMessageView(SuccessMessageMixin, PasswordChangeView):
    success_url = reverse_lazy("index")
    success_message = "The password has been changed successfully."


class NoteCreateView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SuccessMessageMixin,
    CreateView,
):
    model = Note
    form_class = NoteForm
    success_message = "The note has been create successfully"
    template_name = "users/note_create.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"teacher": self.request.user})

        return kwargs

    def get_initial(self):
        return {"student": self.request.GET.get("student")}

    def get_success_url(self):
        return self.object.student.student_detail_url


class NoteDeleteView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    AjaxRequiredMixin,
    DeleteView,
):
    model = Note
    pk_url_kwarg = "note_pk"
    template_name = "users/modals/note_delete.html"
    context_object_name = "note"

    def get_queryset(self):
        return super().get_queryset().visible_to_user(user=self.request.user)

    def get_success_url(self):
        return self.object.student.student_detail_url


class NoteListView(
    LoginRequiredMixin, RolesRequiredMixin(ROLES.STUDENT, ROLES.PARENT), ListView
):
    model = Note
    paginate_by = 10
    ordering = ["-created"]
    template_name = "users/note_list.html"
    context_object_name = "notes"

    def get(self, *args, **kwargs):
        # in template unseen grades are rendered in a different way
        result = super().get(*args, **kwargs)

        if self.request.user.is_parent:
            Note.objects.filter(student__parent=self.request.user).update(
                seen_by_parent=True
            )
        elif self.request.user.is_student:
            Note.objects.filter(student=self.request.user).update(seen_by_student=True)

        return result

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .visible_to_user(user=self.request.user)
            .select_related("teacher")
        )
