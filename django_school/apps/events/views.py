import datetime

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from django_school.apps.events.calendar import EventCalendar
from django_school.apps.events.models import Event


class EventsCalendarView(LoginRequiredMixin, TemplateView):
    template_name = "events/events.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year, month = self.get_year_and_month()
        events = (
            Event.objects.for_year_and_month(year, month)
            .for_user(self.request.user)
            .select_related("school_class", "teacher")
        )
        calendar = EventCalendar(events).formatmonth(year, month)

        context.update(
            {
                "calendar": calendar,
                "year": year,
                "month": month,
            }
        )

        return context

    def get_year_and_month(self):
        today = datetime.date.today()

        try:
            year = int(self.request.GET["year"])
            month = int(self.request.GET["month"])
        except (ValueError, KeyError):
            year = today.year
            month = today.month

        if month > 12:
            year += 1
            month = 1
        elif month < 1:
            year -= 1
            month = 12

        return year, month
