import datetime

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, TemplateView,
                                  UpdateView)

from django_school.apps.common.utils import (AjaxRequiredMixin,
                                             RolesRequiredMixin)
from django_school.apps.events.calendar import EventCalendar
from django_school.apps.events.forms import EventForm
from django_school.apps.events.models import Event, EventStatus
from django_school.apps.users.models import ROLES


class EventsCalendarView(LoginRequiredMixin, TemplateView):
    template_name = "events/events.html"

    def get(self, *args, **kwargs):
        result = super().get(
            *args, **kwargs
        )  # unseen events are rendered in a different way

        year, month = self.get_year_and_month()
        EventStatus.objects.filter(
            user=self.request.user, event__date__year=year, event__date__month=month
        ).update(seen=True)

        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        year, month = self.get_year_and_month()
        events = (
            Event.objects.for_year_and_month(year, month)
            .visible_to_user(self.request.user)
            .with_statuses(self.request.user)
            .select_related("school_class", "teacher")
        )
        calendar = EventCalendar(events, user=self.request.user).formatmonth(
            year, month
        )

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


class EventCreateView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SuccessMessageMixin,
    CreateView,
):
    model = Event
    form_class = EventForm
    success_url = reverse_lazy("events:calendar")
    success_message = "The event has been created successfully"
    template_name = "events/event_form.html"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class EventUpdateView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    SuccessMessageMixin,
    UpdateView,
):
    model = Event
    form_class = EventForm
    pk_url_kwarg = "event_pk"
    success_url = reverse_lazy("events:calendar")
    success_message = "The event has been updated successfully"
    template_name = "events/event_update.html"
    context_object_name = "event"

    def get_queryset(self):
        return super().get_queryset().filter(teacher=self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.update({"user": self.request.user})
        return kwargs


class EventDeleteView(
    LoginRequiredMixin,
    RolesRequiredMixin(ROLES.TEACHER),
    AjaxRequiredMixin,
    DeleteView,
):
    model = Event
    pk_url_kwarg = "event_pk"
    success_url = reverse_lazy("events:calendar")
    success_message = "The event has been deleted successfully."
    template_name = "events/modals/event_delete.html"
    context_object_name = "event"

    def get_queryset(self):
        return super().get_queryset().filter(teacher=self.request.user)

    def delete(self, *args, **kwargs):
        messages.success(self.request, self.success_message)
        return super().delete(*args, **kwargs)
