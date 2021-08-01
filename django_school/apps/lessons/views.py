from django.views.generic import DetailView

from django_school.apps.classes.models import Class
from django_school.apps.lessons.models import LESSONS_TIMES, WEEKDAYS


class TimetableView(DetailView):
    model = Class
    context_object_name = "school_class"
    template_name = "lessons/timetable.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("lessons__subject", "lessons__teacher")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lessons_times"] = LESSONS_TIMES
        context["weekdays"] = WEEKDAYS

        return context
