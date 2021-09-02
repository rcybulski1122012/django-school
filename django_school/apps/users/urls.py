from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from django_school.apps.users.views import (PasswordChangeWithMessageView,
                                            StudentDetailView, profile_view)

app_name = "users"

urlpatterns = [
    path("profile/", profile_view, name="profile"),
    path("login/", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password_change/",
        PasswordChangeWithMessageView.as_view(),
        name="password_change",
    ),
    path("<slug:slug>/", StudentDetailView.as_view(), name="detail"),
]
