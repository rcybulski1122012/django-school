"""django_school URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

from django_school.apps.common.views import attached_file_delete_view

urlpatterns = [
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("users/", include("django_school.apps.users.urls", namespace="users")),
    path("classes/", include("django_school.apps.classes.urls", namespace="classes")),
    path("lessons/", include("django_school.apps.lessons.urls", namespace="lessons")),
    path("grades/", include("django_school.apps.grades.urls", namespace="grades")),
    path(
        "messages/", include("django_school.apps.messages.urls", namespace="messages")
    ),
    path("events/", include("django_school.apps.events.urls", namespace="events")),
    path("admin/", admin.site.urls),
    path("martor/", include("martor.urls")),
    path(
        "attached_files/<int:pk>/delete/",
        attached_file_delete_view,
        name="attached_file_delete",
    ),
    path("__debug__", include(debug_toolbar.urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
