import datetime
from calendar import HTMLCalendar
from collections import defaultdict

from django.template.loader import get_template


class EventCalendar(HTMLCalendar):
    event_template = get_template("events/event.html")
    year = None
    month = None

    cssclass_month = "table table-bordered"
    cssclass_month_head = "text-center"

    def __init__(self, events, user=None):
        self.events = defaultdict(list)
        self.user = user
        for event in events:
            self.events[event.date].append(event)

        super().__init__()

    def formatday(self, day, weekday):
        if not (self.year and self.month) or day == 0:
            return super().formatday(day, weekday)

        current_day = datetime.date(self.year, self.month, day)
        current_day_events = self.events[current_day]
        current_day_events_html = ""

        for event in current_day_events:
            current_day_events_html += self.event_template.render(
                context={"event": event, "user": self.user}
            )

        return f"<td>{day}{current_day_events_html}</td>"

    def formatmonth(self, theyear, themonth, withyear=True):
        self.year = theyear
        self.month = themonth

        return super().formatmonth(theyear, themonth, withyear)
