from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from django_school.apps.users.views import (NoteCreateView, NoteDeleteView,
                                            NoteListView,
                                            PasswordChangeWithMessageView,
                                            SetPasswordView, StudentDetailView)

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        PasswordChangeWithMessageView.as_view(),
        name="password_change",
    ),
    path(
        "password_set/<uidb64>/<token>/", SetPasswordView.as_view(), name="password_set"
    ),
    path(
        "notes/add/",
        NoteCreateView.as_view(),
        name="add_note",
    ),
    path("notes/<int:note_pk>/delete/", NoteDeleteView.as_view(), name="note_delete"),
    path("notes/", NoteListView.as_view(), name="note_list"),
    path("<slug:student_slug>/", StudentDetailView.as_view(), name="detail"),
]
