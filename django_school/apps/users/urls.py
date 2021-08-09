from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from django_school.apps.users.views import UserDetailView, profile_view

app_name = "users"

urlpatterns = [
    path("<int:pk>/", UserDetailView.as_view(), name="detail"),
    path("profile/", profile_view, name="profile"),
    path("login/", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
]
